from typing import List, Optional

from slowbeast.core.errors import GenericError, MemError
from slowbeast.domains.concrete import concrete_value
from slowbeast.ir.instruction import Alloc, Instruction, Load, Store, ThreadJoin, Return, Thread
from slowbeast.ir.types import get_offset_type
from slowbeast.symexe.iexecutor import IExecutor as BaseIExecutor
from slowbeast.symexe.memorymodel import SymbolicMemoryModel
from slowbeast.symexe.threads.state import TSEState
from slowbeast.util.debugging import ldbgv, dbgv


def may_be_glob_mem(state, mem: Alloc) -> bool:
    ptr = state.try_eval(mem)
    if ptr and ptr.object().is_concrete():
        mo = state.memory.get_obj(ptr.object())
        if mo is None:
            return True
        if mo.is_read_only():
            # read only objects cannot be modified and so we do not care about them
            return False
        return mo.is_global() or mo.is_heap()

    return True


class IExecutor(BaseIExecutor):
    def __init__(
        self, program, solver, opts, memorymodel: Optional[SymbolicMemoryModel] = None
    ) -> None:
        super().__init__(program, solver, opts, memorymodel)
        self.check_race = False

    def create_state(self, pc=None, m=None) -> TSEState:
        if m is None:
            m = self.get_memory_model().create_memory()
        # if self.get_options().incremental_solving:
        #    return IncrementalSEState(self, pc, m)
        return TSEState(self, pc, m, self.solver)

    def exec_undef_fun(self, state, instr, fun):
        fnname = fun.name()
        if fnname == "__VERIFIER_atomic_begin":
            state.start_atomic()
            state.pc = state.pc.get_next_inst()
            return [state]
        if fnname == "__VERIFIER_atomic_end":
            state.end_atomic()
            state.pc = state.pc.get_next_inst()
            return [state]
        if fnname == "pthread_mutex_init":
            state.mutex_init(state.eval(instr.operand(0)))
            # return non-det value for the init
            # TODO: we should connect the returned value with the
            # effect of init...
            return super().exec_undef_fun(state, instr, fun)
        if fnname == "pthread_mutex_destroy":
            state.mutex_destroy(state.eval(instr.operand(0)))
            # the same as for init...
            return super().exec_undef_fun(state, instr, fun)
        if fnname == "pthread_mutex_lock":
            mtx = state.eval(instr.operand(0))
            # TODO: This does not work with mutexes initialized via assignment...
            # if not state.has_mutex(mtx):
            #    state.set_killed("Locking unknown mutex")
            #    return [state]
            lckd = state.mutex_locked_by(mtx)
            if lckd is not None:
                if lckd == state.thread().get_id():
                    state.set_killed("Double lock")
                else:
                    state.mutex_wait(mtx)
            else:
                state.mutex_lock(mtx)
                state.pc = state.pc.get_next_inst()
            return [state]
        if fnname == "pthread_mutex_unlock":
            mtx = state.eval(instr.operand(0))
            if not state.has_mutex(mtx):
                state.set_killed("Unlocking unknown mutex")
                return [state]
            lckd = state.mutex_locked_by(mtx)
            if lckd is None:
                state.set_killed("Unlocking unlocked lock")
            else:
                if lckd != state.thread().get_id():
                    state.set_killed("Unlocking un-owned mutex")
                else:
                    state.mutex_unlock(mtx)
                    state.pc = state.pc.get_next_inst()
            return [state]
        if fnname.startswith("pthread_"):
            state.set_killed(f"Unsupported pthread_* API: {fnname}")
            return [state]
        return super().exec_undef_fun(state, instr, fun)

    def call_fun(self, state, instr, fun):
        if fun.name().startswith("__VERIFIER_atomic_"):
            state.start_atomic()
        return super().call_fun(state, instr, fun)

    def exec_thread(self, state, instr):
        fun = instr.called_function()
        ldbgv("-- THREAD {0} --", (fun.name(),))
        if fun.is_undefined():
            state.set_error(
                GenericError(f"Spawning thread with undefined function: {fun.name()}")
            )
            return [state]
        # map values to arguments
        # TODO: do we want to allow this? Less actual parameters than formal parameters?
        # assert len(instr.operands()) == len(fun.arguments())
        if len(instr.operands()) > len(fun.arguments()):
            dbgv(
                "Thread created with less actual arguments than with formal arguments..."
            )
        assert len(instr.operands()) >= len(fun.arguments())
        mapping = {
            x: state.eval(y) for (x, y) in zip(fun.arguments(), instr.operands())
        }
        t = state.add_thread(fun, fun.bblock(0).instruction(0), mapping or {})

        state.pc = state.pc.get_next_inst()
        state.set(instr, concrete_value(t.get_id(), get_offset_type()))
        # newstate.set(instr, concrete_value(t.get_id(), get_offset_type()))
        return [state]

    def exec_thread_join(self, state, instr: ThreadJoin):
        assert len(instr.operands()) == 1
        tid = state.eval(instr.operand(0))
        if not tid.is_concrete():
            state.set_killed("Symbolic thread values are unsupported yet")
        else:
            state.join_threads(tid.value())
        return [state]

    def exec_ret(self, state, instr: Return):
        # obtain the return value (if any)
        ret = None
        if len(instr.operands()) != 0:  # returns something
            ret = state.eval(instr.operand(0))
            assert (
                ret is not None
            ), f"No return value even though there should be: {instr}"

        if state.frame().function.name().startswith("__VERIFIER_atomic_"):
            state.end_atomic()
        # pop the call frame and get the return site
        rs = state.pop_call()
        if rs is None:  # popped the last frame
            state.exit_thread(ret)
            return [state]

        if ret:
            state.set(rs, ret)

        state.pc = rs.get_next_inst()
        return [state]

    def execute(self, state: TSEState, instr: Instruction) -> List[Optional[TSEState]]:

        if state.num_threads() == 0:
            return []
        
        self.check_race = state.race_condition_possible() and 'no-data-race' in self._opts.check
        
        # We explore all possible interleavings. DFS - Right to Left.
        # Each instruction will return the number of active threads times the usual number of returned states.
        # - For each active non-atomic thread: (Since unpausing is done by active threads, we don't have to execute them)
        #   - Clone the state.
        #   - Schedule the thread in this state.
        #   - push the returned output states in the output stack.
        # - Return the stack.
        # instr is irrelevant.
        states = []
        for t in state.threads():
            if not t.is_paused():
                s = state.copy()    # Copy even when just one thread. Inefficient. XXX
                s.schedule(t.get_id())
                self.check_race = self.check_race and not t.in_atomic()
                states += self.execute_single_thread(s, s.pc)
                for ns in states:
                    ns.sync_pc()
                    ns.sync_cs()
        return states
    
    def execute_single_thread(self, state: TSEState, instr: Instruction) -> List[TSEState]:
        if isinstance(instr, Thread):
            return self.exec_thread(state, instr)
        if isinstance(instr, ThreadJoin):
            return self.exec_thread_join(state, instr)
        if isinstance(instr, Return):
            return self.exec_ret(state, instr)
        if self.check_race:
            if isinstance(instr, Store):
                return self.tainted_write(state, instr)
            elif isinstance(instr, Load):
                return self.tainted_read(state, instr)

        return super().execute(state, instr)

    def tainted_read(self, state: TSEState, instr: Load):
        if instr.pointer_operand() in state._tainted_locations:
            err = MemError(MemError.DATA_RACE, " DATA RACE DETECTED: " + str(instr.pointer_operand()))
            state.set_error(err)
            return state
        else:
            return super().execute(state, instr)

    def tainted_write(self, state: TSEState, instr: Store):
        if instr.pointer_operand() in state._tainted_locations:
            err = MemError(MemError.DATA_RACE, " DATA RACE DETECTED: " + str(instr.pointer_operand()))
            state.set_error(err)
            return state
        else:
            if may_be_glob_mem(state, instr.pointer_operand()):
                state._tainted_locations.append(instr.pointer_operand())
            return super().execute(state, instr)

    # def exec_thread_exit(self, state, instr: ThreadExit):
    #    assert isinstance(instr, ThreadExit)

    #    # obtain the return value (if any)
    #    ret = None
    #    if len(instr.operands()) != 0:  # returns something
    #        ret = state.eval(instr.operand(0))
    #        assert (
    #            ret is not None
    #        ), f"No return value even though there should be: {instr}"

    #    state.exit_thread(ret)
    #    return [state]
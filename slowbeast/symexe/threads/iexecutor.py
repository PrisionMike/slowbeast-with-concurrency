from __future__ import annotations

from slowbeast.core.errors import GenericError
from slowbeast.domains.concrete import concrete_value
from slowbeast.ir.instruction import Alloc, ThreadJoin, Return, Thread, Call
from slowbeast.ir.types import get_offset_type
from slowbeast.ir.function import Function
from slowbeast.symexe.iexecutor import IExecutor as BaseIExecutor, unsupported_funs

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
        self,
        program,
        solver,
        opts,
        memorymodel: SymbolicMemoryModel | None = None,  # noqa:F821
    ) -> None:
        super().__init__(program, solver, opts, memorymodel)

    def exec_undef_fun(self, state, instr, fun, tid):
        fnname = fun.name()
        state.pc = state.thread(tid).pc
        state.memory.set_cs(state.thread(tid).get_cs())
        outputs = []
        final_result = []

        if fnname == "__VERIFIER_atomic_begin":
            state.start_atomic(tid)
            state.thread(tid).pc = instr.get_next_inst()
            return [state], instr
        elif fnname == "__VERIFIER_atomic_end":
            state.end_atomic(tid)
            state.thread(tid).pc = instr.get_next_inst()
            return [state], instr
        elif fnname == "pthread_mutex_init":
            # return non-det value for the init
            # mchalupa: TODO: we should connect the returned value with the
            # effect of init...
            state.mutex_init(state.eval(instr.operand(0)))
            outputs = super().exec_undef_fun(state, instr, fun)
        elif fnname == "pthread_mutex_destroy":
            # mchalupa: the same as for init...
            state.mutex_destroy(state.eval(instr.operand(0)))
            outputs = super().exec_undef_fun(state, instr, fun)
        elif fnname == "pthread_mutex_lock":
            mtx = state.eval(instr.operand(0))
            # mchalupa TODO: This does not work with mutexes initialized via assignment...
            lckd = state.mutex_locked_by(mtx)
            if lckd is not None:
                # if lckd == state.thread().get_id():
                if lckd == tid:
                    state.set_killed("Double lock")
                else:
                    state.mutex_wait(mtx, tid)
            else:
                state.mutex_lock(mtx, tid)
                state.thread(tid).pc = instr.get_next_inst()
                instr.succ = True
            return [state], instr  # XXX
        elif fnname == "pthread_mutex_unlock":
            mtx = state.eval(instr.operand(0))
            if not state.has_mutex(mtx):
                state.set_killed("Unlocking unknown mutex")
                return [state], instr
            lckd = state.mutex_locked_by(mtx)
            if lckd is None:
                state.set_killed("Unlocking unlocked lock")
            else:
                # if lckd != state.thread().get_id():
                if lckd != tid:
                    state.set_killed("Unlocking un-owned mutex")
                else:
                    state.mutex_unlock(mtx, tid)
                    state.thread(tid).pc = instr.get_next_inst()
            return [state], instr
        elif fnname.startswith("pthread_"):
            state.set_killed(f"Unsupported pthread_* API: {fnname}")
            return [state], instr
        else:
            outputs = super().exec_undef_fun(state, instr, fun)

        for output_state in outputs:
            output_state.thread(tid).pc = output_state.pc
            output_state.thread(tid).set_cs(output_state.memory.get_cs())
            final_result.append(output_state)
        return final_result, instr

    def exec_call(
        self, state: SEState, instr: Call, tid
    ) -> tuple[List[SEState], Instruction]:
        fun = instr.called_function()
        if not isinstance(fun, Function):
            fun = self._resolve_function_pointer(state, fun)
            if fun is None:
                state.set_killed(
                    f"Failed resolving function pointer: {instr.called_function()}"
                )
                return [state], instr
            assert isinstance(fun, Function)

        if self.is_error_fn(fun):
            state.set_error(AssertFailError(f"Called '{fun.name()}'"))
            return [state], instr

        if fun.is_undefined():
            name = fun.name()
            if name == "abort":
                state.set_terminated("Aborted via an abort() call")
                return [state], instr
            if name in ("exit", "_exit"):
                state.set_exited(state.eval(instr.operand(0)))
                return [state], instr
            if name in unsupported_funs:
                state.set_killed(f"Called unsupported function: {name}")
                return [state], instr
            return self.exec_undef_fun(state, instr, fun, tid)

        if self.calls_forbidden():
            # mchalupa: TODO: make this more fine-grained, which calls are forbidden?
            state.set_killed(f"calling '{fun.name()}', but calls are forbidden")
            return [state]

        return self.call_fun(state, instr, fun, tid)

    def call_fun(self, state, instr, fun, tid) -> list[TSEState]:
        if fun.name().startswith("__VERIFIER_atomic_"):
            state.start_atomic(tid)
        state.pc = state.thread(tid).pc
        state.memory.set_cs(state.thread(tid).get_cs())
        outputs = super().call_fun(state, instr, fun)
        final_result = []
        for output_state in outputs:
            output_state.thread(tid).pc = output_state.pc
            output_state.thread(tid).set_cs(output_state.memory.get_cs())
            final_result.append(output_state)
        return final_result

    def exec_thread(self, state, instr, tid) -> list[TSEState]:  # type: ignore
        fun = instr.called_function()
        ldbgv("-- THREAD {0} --", (fun.name(),))
        if fun.is_undefined():
            state.set_error(
                GenericError(f"Spawning thread with undefined function: {fun.name()}")
            )
            return [state]
        if len(instr.operands()) > len(fun.arguments()):
            dbgv(
                "Thread created with less actual arguments than with formal arguments..."
            )
        assert len(instr.operands()) >= len(fun.arguments())
        mapping = {
            x: state.eval(y) for (x, y) in zip(fun.arguments(), instr.operands())
        }
        t = state.add_thread(fun, fun.bblock(0).instruction(0), mapping or {})

        instr._operand_tid = t.get_id()

        state.thread(tid).pc = instr.get_next_inst()
        state.thread(tid).get_cs().set(
            instr, concrete_value(t.get_id(), get_offset_type())
        )
        return [state]

    def exec_thread_join(self, state, instr: ThreadJoin, totid) -> list[TSEState]:
        assert len(instr.operands()) == 1
        tid = state.eval(instr.operand(0))
        instr._operand_tid = tid.value()
        if not tid.is_concrete():
            state.set_killed("Symbolic thread values are unsupported yet")
        else:
            state.join_threads(tid.value(), totid)
        return [state]

    def exec_ret(self, state, instr: Return, tid) -> list[TSEState]:
        # obtain the return value (if any)
        ret = None
        if len(instr.operands()) != 0:  # returns something
            ret = state.eval(instr.operand(0))
            assert (
                ret is not None
            ), f"No return value even though there should be: {instr}"

        if (
            state.thread(tid)
            .get_cs()
            .frame()
            .function.name()
            .startswith("__VERIFIER_atomic_")
        ):
            state.end_atomic(tid)
        # pop the call frame and get the return site
        rs = state.thread(tid).get_cs().pop_call()
        if rs is None:  # popped the last frame
            state.exit_thread(ret, tid)
            return [state]

        if ret:
            state.thread(tid).get_cs().set(rs, ret)

        state.thread(tid).pc = rs.get_next_inst()
        return [state]

    def execute(self, state: TSEState) -> list[TSEState]:

        states = []
        if state.num_threads() == 0:
            return states

        for t in state._threads:
            if not state.thread(t).is_paused():
                states.append(self.execute_single_thread(state, t))
                for ns in states:
                    ns.sync_pc()
                    ns.sync_cs()
        return states

    def wrapper_for_legacy(self, state: TSEState, tid: int) -> list[TSEState]:
        """Should be made into a decorator or accept calling function as an argument. TODO"""
        state.pc = state.thread(tid).pc
        state.memory.set_cs(state.thread(tid).get_cs())
        outputs = self.exec_legacy(state, state.pc)
        states = []
        for legacy_output in outputs:
            legacy_output.thread(tid).pc = legacy_output.pc
            legacy_output.thread(tid).set_cs(legacy_output.memory.get_cs())
            states.append(legacy_output)
        return states

    def execute_single_thread(
        self, state: TSEState, thread_id: int
    ) -> tuple[list[TSEState], Instruction]:
        s = state.copy()
        instr = s.thread(thread_id).pc
        if isinstance(instr, Thread):
            return self.exec_thread(s, instr, thread_id), instr
        if isinstance(instr, ThreadJoin):
            return self.exec_thread_join(s, instr, thread_id), instr
        if isinstance(instr, Return):
            return self.exec_ret(s, instr, thread_id), instr
        if isinstance(instr, Call):
            return self.exec_call(s, instr, thread_id)

        return self.wrapper_for_legacy(s, thread_id), instr

    def exec_legacy(self, state, instr):
        return super().execute(state, instr)

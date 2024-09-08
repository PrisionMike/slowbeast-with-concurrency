from typing import List, Optional, Union

from slowbeast.core.errors import GenericError
from slowbeast.interpreter.interpreter import GlobalInit
from slowbeast.ir.function import Function
from slowbeast.ir.instruction import Alloc, Call, Load, Store, ThreadJoin, Thread
from slowbeast.symexe.interpreter import SymbolicInterpreter as SymexeInterpreter
from slowbeast.symexe.options import SEOptions
from slowbeast.symexe.state import SEState
from slowbeast.symexe.threads.iexecutor import IExecutor, may_be_glob_mem
from slowbeast.symexe.threads.state import TSEState
from slowbeast.util.debugging import print_stderr


def _is_global_event_fun(fn) -> bool:
    # FIXME: what if another thread is writing to arguments of pthread_create?
    # return name.startswith("pthread_")  or
    # name.startswith("__VERIFIER_atomic")
    name = fn.name()
    if name.startswith("__VERIFIER_atomic"):
        return True
    if fn.is_undefined() and name in (
        "pthread_mutex_lock",
        "pthread_mutex_unlock",
    ):
        return True
    return False


class SymbolicInterpreter(SymexeInterpreter):
    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        super().__init__(P, ohandler, opts, ExecutorClass=IExecutor)

    def _is_global_event(self, state, pc: Union[Call, Load, Store, ThreadJoin]) -> bool:
        if isinstance(pc, Load):
            return may_be_glob_mem(state, pc.operand(0))
        if isinstance(pc, Store):
            return may_be_glob_mem(state, pc.operand(1))
        if isinstance(pc, (Thread, ThreadJoin)):
            return True
        if isinstance(pc, Call):
            fn = pc.called_function()
            if not isinstance(fn, Function):
                fun = state.try_eval(fn)
                if fun is None:
                    return True
                fn = self.executor()._resolve_function_pointer(state, fun)
                if fn is None:
                    return True
                assert isinstance(fn, Function)
            return _is_global_event_fun(fn)
        return False

    # def schedule(self, state: TSEState) -> List[Optional[TSEState]]:
    #     l = state.num_threads()
    #     if l == 0:
    #         return []
    #     # if the thread is in an atomic sequence, continue it...
    #     t = state.thread()
    #     if t.in_atomic():
    #         if not t.is_paused():
    #             return [state]
    #         # this thread is dead-locked, but other can continue
    #         state.set_killed(
    #             f"Thread {t.get_id()} is stuck "
    #             "(waits for a mutex inside an atomic sequence)"
    #         )
    #         return [state]

    #     # is_global_ev = self._is_global_event
    #     # for idx, t in enumerate(state.threads()):
    #     #     if t.is_paused():
    #     #         continue
    #     #     if not is_global_ev(state, t.pc):
    #     #         state.schedule(idx)  
    #     #         return [state]  # XXX Seems problematic

    #     can_run = [idx for idx, t in enumerate(state.threads()) if not t.is_paused()]
    #     if len(can_run) == 0:
    #         state.set_error(GenericError("Deadlock detected"))
    #         return [state]
    #     if len(can_run) == 1:
    #         state.schedule(can_run[0])
    #         return [state]

    #     states = []
    #     for idx in can_run:
    #         s = state.copy()
    #         s.schedule(idx)
    #         states.append(s)
    #     assert states
    #     return states

    def prepare(self) -> None:
        """
        Prepare the interpreter for execution.
        I.e. initialize static memory and push the call to
        the main function to call stack.
        Result is a set of states before starting executing
        the entry function.
        """
        self.states = self.initial_states()
        self.run_static()

        # push call to main to call stack
        entry = self.get_program().entry()
        for s in self.states:
            s.push_call(None, entry)
            main_args = self._main_args(s)
            assert s.num_threads() == 1
            if main_args:
                s.memory.get_cs().set_values(main_args)
            s.sync_pc()

    def check_deadlock(self, state) -> None:
        """Kills the state if it is in deadlock"""
        if state.thread().in_atomic() and state.thread().is_paused():
            state.set_killed(
            f"Thread {state.thread().get_id()} is stuck "
            "(waits for a mutex inside an atomic sequence)"
            )

    def run(self) -> int:
        self.prepare()

        # we're ready to go!
        try:
            mhare_pyare_states = []
            while self.states:
                print("-------------------------")
                print("On the tree:", [x.get_id() for x in self.states])
                newstates = []
                state = self.get_next_state()
                print("Parent (being executed):", state._id)
                self.check_deadlock(state)
                self.interact_if_needed(state)
                # state.get_id() in (121,156,157,184,185,158,165,171) # (state.get_id() >= 171) or 
                # state.get_id() % 1000 == 0 and state.get_id() >= 4000 
                if state.is_ready():
                    newstates += self._executor.execute(state, state.pc) 
                else:
                    newstates.append(state)
                print("Children:",[(x.get_id(), x.status()) for x in newstates])
                self.handle_new_states(newstates)
                for ns in newstates:
                    if ns.exited():
                        mhare_pyare_states.append(ns.get_id())

        except Exception as e:
            print_stderr(f"Fatal error while executing '{state.pc}'", color="red")
            state.dump()
            raise e

        self.report()

        return 0


def events_conflict(events, othevents) -> bool:
    for ev in (
        e
        for e in events
        if not e.is_call_of(("__VERIFIER_atomic_begin", "__VERIFIER_atomic_end"))
    ):
        for oev in (
            e
            for e in othevents
            if not e.is_call_of(("__VERIFIER_atomic_begin", "__VERIFIER_atomic_end"))
        ):
            if ev.conflicts(oev):
                return True
    return False


def has_conflicts(state, events, states_with_events) -> bool:
    for _, othstate, othevents in states_with_events:
        if state is othstate:
            continue
        if events_conflict(events, othevents):
            return True
    return False


class DPORSymbolicInterpreter(SymbolicInterpreter):

    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        super().__init__(P, ohandler, opts)
        print("Running symbolic execution with DPOR")

    def get_extended_states(self) -> TSEState:
        pass

    def get_enabled_states(self) -> TSEState:
        pass

    def run(self) -> int:
        self.prepare()
        self.executing_state = self.get_executing_state() # C
        self.avoiding_state = self.get_avoiding_state() # D
        self.assisting_state = self.get_assisting_state() # A
        self.master_state = self.get_master_state() # U

        self.explore()
    
    def explore(self) -> None:
        """ Tentative 'run' command."""
        self.master_state.extend(self.executing_state.get_extented_instructions())
        
        enabled_in_c = self.executing_state.get_enabled_instructions()
        if enabled_in_c.len() == 0 \
            or enabled_in_c is None:
            return
        
        state_a = self.get_assisting_state()
        if state_a is None:
            exec_instruction = enabled_in_c[0]
        else:
            for e in state_a.trace:
                if e in enabled_in_c:
                    exec_instruction = e
                    break
        assert exec_instruction is not None, "event not chosen properly in Explore"
        
        
        
    

    def prepare(self) -> None:
        # Should set explore to {phi phi phi}
        self.executing_state = None
        self.avoiding_state = None
        self.assisting_state = None
        self.master_state = self._executor.create_state() # Should be initial state.
        
        # Copied from parent class.
        # push call to main to call stack
        entry = self.get_program().entry()
        self.master_state.push_call(None, entry)
        main_args = self._main_args(self.master_state)
        assert self.master_state.num_threads() == 1
        if main_args:
            self.master_state.get_cs().set_values(main_args)
        self.master_state.sync_pc()
        self.run_static()
    
    def run_static(self) -> None:
        """Run static actors (e.g. initialize globals)"""
        # fake the program counter for the executor
        ginit = GlobalInit()

        self.master_state.pc = ginit

        globs = self._program.globals()
        for G in globs:
            # bind the global to the state
            self.master_state.memory.allocate_global(G, zeroed=G.is_zeroed())

            if not G.has_init():
                continue
            for i in G.init():
                # Hack for concurrent program: FIXME
                if self.get_options().threads:
                    ret = self._executor.execute_single_thread(self.master_state, i)
                else:
                    ret = self._executor.execute(self.master_state, i)
                assert len(ret) == 1, "Unhandled initialization"
                assert ret[
                    0
                ].is_ready(), (
                    "Generated errorneous state during initialization of globals"
                )
                    
    # Set C
    def get_executing_state(self) -> TSEState:
        pass

    # Set A in the algorithm
    def get_assisting_state(self) -> TSEState:
        pass

    # Set D
    def get_avoiding_state(self) -> TSEState:
        pass

    # Set U
    def get_master_state(self) -> TSEState:
        pass

    # Set G
    def get_deletable_states(self) -> TSEState:
        pass
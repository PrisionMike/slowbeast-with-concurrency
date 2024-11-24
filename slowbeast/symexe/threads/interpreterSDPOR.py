from __future__ import annotations

# from typing import Set
from slowbeast.symexe.options import SEOptions

# from slowbeast.symexe.threads.configuration import Configuration
from slowbeast.symexe.threads.interpreter import SymbolicInterpreter
from slowbeast.symexe.threads.state import TSEState
from slowbeast.interpreter.interpreter import GlobalInit

# For debugger:
from slowbeast.ir.instruction import Call  # noqa:F401

# from slowbeast.symexe.threads.iexecutor import IExecutor


class SPORSymbolicInterpreter(SymbolicInterpreter):

    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        print("Initiating the SPOR executor")
        super().__init__(P, ohandler, opts)

    def initial_states(self) -> TSEState:
        mem = self._executor.get_memory_model().create_memory()
        return TSEState(self._executor, None, mem, self._executor.solver)

    def prepare(self) -> None:
        """
        DUPLICATED FROM PREDECESSOR
        Initial state no longer a list.
        TODO: Move such changes upstream.
        Prepare the interpreter for execution.
        I.e. initialize static memory and push the call to
        the main function to call stack.
        Result is a set of states before starting executing
        the entry function.
        """
        self.init_state = self.initial_states()
        self.run_static()

        # push call to main to call stack
        entry = self.get_program().entry()
        self.init_state.push_call(None, entry)
        main_args = self._main_args(self.init_state)
        assert self.init_state.num_threads() == 1
        if main_args:
            self.init_state.memory.get_cs().set_values(main_args)
        self.init_state.sync_pc()

    def run_static(self) -> None:
        """
        DUPLICATED to resolve initial states being a list.
        Run static actors (e.g. initialize globals)
        """
        # fake the program counter for the executor
        ginit = GlobalInit()
        self.init_state.pc = ginit

        globs = self._program.globals()
        for G in globs:
            # bind the global to the state
            self.init_state.memory.allocate_global(G, zeroed=G.is_zeroed())

            if not G.has_init():
                continue
            for i in G.init():
                # Hack for concurrent program: FIXME
                if self.get_options().threads:
                    ret = self._executor.exec_legacy(self.init_state, i)
                    # ret = self._executor.execute(self.init_state, i)
                else:
                    ret = self._executor.exec_legacy(self.init_state, i)
                assert len(ret) == 1, "Unhandled initialization"
                # assert ret[0] is s, "Unhandled initialization instruction"
                assert ret[
                    0
                ].is_ready(), (
                    "Generated errorneous state during initialization of globals"
                )

    def run(self) -> int:
        self.prepare()
        # self.init_state: TSEState = self.initial_states()
        self.trace = self.init_state.trace  # Empty trace
        self.explore(self.init_state, set())

    def explore(self, state: TSEState, sleep: set) -> None:
        """Source - DPOR"""
        enabled_set = get_enabled_threads(state)
        usable_threads = enabled_set.difference(sleep)
        if usable_threads:
            self.trace.set_backtrack(
                {usable_threads.pop()}
            )  # Isolate trace from state execution TODO: remove all trace references from the state.
            while state.trace.get_backtrack().difference(sleep):
                ithread = state.trace.get_backtrack().difference(sleep).pop()
                ithread_in_action = state.thread_to_action(ithread)
                if ithread_in_action is not None:
                    extended_trace = state.trace.append(
                        ithread_in_action
                    )  # This should handle updating causality and race.
                    for racist_action in extended_trace.get_racist_set():
                        indep_suffix_set = extended_trace.independent_suffix_set(
                            racist_action
                        )
                        racist_prefix_backtrack = extended_trace.get_backtrack(
                            racist_action
                        )
                        if not indep_suffix_set.intersection(racist_prefix_backtrack):
                            extended_trace.add_to_prefix_backtrack(
                                racist_action, indep_suffix_set.pop()
                            )
                    newstates = state.exec_trace(extended_trace)
                    for s in newstates:
                        s.check_data_race()
                        self.handle_new_state(s)
                        newsleep = set()
                        for q in sleep:
                            if not dependent_threads(s, ithread, q):
                                newsleep.add(q)
                        # if s.is_ready():
                        self.explore(s, newsleep)
                        sleep.add(ithread)


def dependent_threads(pstate: TSEState, p: int, q: int) -> bool:
    """pstate = state with p executed. TODO: very inefficient. You just need to check it with the previous instruction"""
    if p == q:
        return True
    if q not in get_enabled_threads(pstate):
        return False
    else:
        q_in_action = pstate.thread_to_action(q)
        pqtrace = pstate.trace.append(q_in_action)
        if pqtrace.sequence[-2] in pqtrace.sequence[-1].caused_by:
            return True
        else:
            return False


def get_enabled_threads(state: TSEState) -> set[int]:
    enabled = set()
    for id in state.thread_ids():
        if not (state.thread(id).is_paused() or state.thread(id).is_detached()):
            enabled.add(id)
    # TODO: make sure threads waiting to be joined are not included as well.
    return enabled

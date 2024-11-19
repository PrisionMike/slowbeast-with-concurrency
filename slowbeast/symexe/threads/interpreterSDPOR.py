from __future__ import annotations

# from typing import Set
from slowbeast.symexe.options import SEOptions

# from slowbeast.symexe.threads.configuration import Configuration
from slowbeast.symexe.threads.interpreter import SymbolicInterpreter
from slowbeast.symexe.threads.state import TSEState
from slowbeast.interpreter.interpreter import GlobalInit


class SPORSymbolicInterpreter(SymbolicInterpreter):

    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        print("Initiating the SPOR executor")
        super().__init__(P, ohandler, opts, None)

    def initial_states(self) -> TSEState:
        mem = self._executor.get_memory_model().create_memory()
        return TSEState(self.executor, None, mem, self._executor.solver)

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
        main_args = self._main_args(s)
        assert self.init_state.num_threads() == 1
        if main_args:
            s.memory.get_cs().set_values(main_args)
        s.sync_pc()

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
                    ret = self._executor.execute_single_thread(self.init_state, i)
                else:
                    ret = self._executor.execute(self.init_state, i)
                assert len(ret) == 1, "Unhandled initialization"
                # assert ret[0] is s, "Unhandled initialization instruction"
                assert ret[
                    0
                ].is_ready(), (
                    "Generated errorneous state during initialization of globals"
                )

    def run(self) -> int:
        self.prepare()
        self.init_state: TSEState = self.initial_states()

        self.explore(self.init_state, set())

    def explore(self, state: TSEState, sleep: set) -> None:
        """Source - DPOR. We don't evaluate causal relation with actions in pc but we can. TODO"""
        enabled = get_enabled_threads(state)
        current_trace = state.trace
        for thread in enabled.difference(sleep):
            current_trace.backtrack = set(thread)
            for ithread in current_trace.backtrack.difference(sleep):
                extended_trace = current_trace.append(
                    ithread
                )  # FIXME convert to action.
                sample_state = (
                    newstates.pop()
                )  # All output states will have the same trace. We just need one.
                ctrace = sample_state.trace
                newstates.add(sample_state)
                for racist_action in ctrace.racist:
                    godfather = ctrace.godfathers(racist_action)
                    prefix_event = ctrace.preceding_action(racist_action)
                    if not godfather.intersection(prefix_event.backtrack):
                        prefix_event.backtrack.add(godfather.pop())
                for s in newstates:
                    s.trace = ctrace
                    newsleep = set()
                    for q in sleep:
                        if not dependent_threads(s, thread, q):
                            newsleep.add(q)
                    self.explore(s, newsleep)
                    sleep.add(thread)


def dependent_threads(pstate: TSEState, p: int, q: int) -> bool:
    """pstate = state with p executed. pqstate wasted. TODO optimise."""
    if p == q:
        return True
    if q not in get_enabled_threads(pstate):
        return False
    else:
        pqstate = pstate.exec(q)
        if pqstate.trace[-2] in pqstate.trace[-1].caused_by:
            return True
        else:
            return False


def get_enabled_threads(state: TSEState) -> set[int]:
    enabled = set()
    for thread in state.threads():
        if not thread.is_paused():
            enabled.add(thread)
    # TODO: make sure threads waiting to be joined are not included as well.
    return enabled

from __future__ import annotations

# from copy import deepcopy
from sys import setrecursionlimit

from slowbeast.symexe.options import SEOptions
from slowbeast.symexe.threads.interpreter import SymbolicInterpreter
from slowbeast.symexe.threads.state import TSEState
from slowbeast.interpreter.interpreter import GlobalInit


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
        # self.trace = self.init_state.trace  # Empty trace

        self.log_trace = []
        self.states.append(
            self.init_state
        )  # To populate self.states to halt exploration
        setrecursionlimit(10**4)
        try:
            self.explore(self.init_state, set())
        except RecursionError:
            print(
                "Exploration too deep. Consider making it iterative or increasing recursion depth."
            )
        print(self.log_trace)

    def explore(self, state: TSEState, sleep: set) -> None:
        """Source - DPOR"""

        if not self.states:
            # Halt. state not ready and has errors.
            self.log_trace.append("⛔")
            return

        enabled_set = get_enabled_threads(state)
        usable_threads = enabled_set.difference(sleep)

        if enabled_set and not usable_threads:
            self.log_trace.append((enabled_set.copy(), "💤🫷", sleep))

        if usable_threads:
            state.trace.set_backtrack({usable_threads.pop()})
            while state.trace.get_backtrack().difference(sleep):
                ithread = state.trace.get_backtrack().difference(sleep).pop()
                ithread_in_action = state.thread_to_action(ithread)
                assert ithread_in_action is not None, "AHHHHHH!!!!!"
                state.trace.append_in_place(
                    ithread_in_action
                )  # This should handle updating causality and race.

                # self.log_trace.append("👇")

                self.log_trace.append(
                    (
                        (ithread_in_action.tid, ithread_in_action.occurrence),
                        state.trace._backtrack[-2],
                        sleep.copy(),
                        ithread_in_action.instr,
                    )
                )

                for racist_action in state.trace.get_racist_set():
                    indep_suffix_set = state.trace.independent_suffix_set(racist_action)
                    racist_prefix_backtrack = state.trace.get_backtrack(racist_action)
                    missing_thread_in_backtrack = None
                    if not indep_suffix_set.intersection(racist_prefix_backtrack):
                        missing_thread_in_backtrack = indep_suffix_set.pop()
                        state.trace.add_to_prefix_backtrack(
                            racist_action, missing_thread_in_backtrack
                        )
                if state.trace.get_racist_set():
                    self.log_trace.append(
                        (
                            "🏁⤴️",
                            [
                                (x.tid, x.occurrence)
                                for x in state.trace.get_racist_set()
                            ],
                            (
                                missing_thread_in_backtrack
                                if missing_thread_in_backtrack
                                else "💩"
                            ),
                        )
                    )
                newstates = state.exec_trace_preset()
                for s in newstates:
                    s.check_data_race()
                    self.handle_new_state(s)
                    newsleep = set()
                    for q in sleep:
                        if not self.dependent_threads(s, ithread, q):
                            newsleep.add(q)
                    if newsleep:
                        self.log_trace.append("💤 : " + str(newsleep.copy()))
                    self.explore(s, newsleep)
                    state.trace.trim()  # Restore original trace (E)

                    self.log_trace.append(("☝️", ithread))

                    sleep.add(ithread)

    def dependent_threads(self, pstate: TSEState, p: int, q: int) -> bool:
        """pstate = state with p executed"""
        if p == q:
            return True
        if q not in get_enabled_threads(pstate):
            return False
        else:
            q_in_action = pstate.thread_to_action(q)
            return pstate.trace.depends_on_last(q_in_action)
            # q_in_action = pstate.thread_to_action(q)
            # pqtrace = deepcopy(pstate.trace)
            # pqtrace.append_in_place(q_in_action)
            # if pqtrace._sequence[-2] in pqtrace._sequence[-1].caused_by:
            #     return True
            # else:
            #     return False


def get_enabled_threads(state: TSEState) -> set[int]:
    if state.is_ready():
        enabled = set()
        for id in state.thread_ids():
            if not (state.thread(id).is_paused() or state.thread(id).is_detached()):
                enabled.add(id)
        return enabled
    else:
        return set()

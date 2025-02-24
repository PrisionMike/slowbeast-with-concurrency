from __future__ import annotations

# from typing import Set
from slowbeast.symexe.options import SEOptions
from slowbeast.symexe.threads.configuration import Configuration
from slowbeast.symexe.threads.interpreter import SymbolicInterpreter
from slowbeast.symexe.threads.state import TSEState
from slowbeast.interpreter.interpreter import GlobalInit


class PORSymbolicInterpreter(SymbolicInterpreter):

    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        print("Initiating the UPOR executor")
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
        self.bot_state = self.initial_states()
        self.run_static()

        # push call to main to call stack
        entry = self.get_program().entry()
        self.bot_state.push_call(None, entry)
        main_args = self._main_args(s)
        assert self.bot_state.num_threads() == 1
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
        self.bot_state.pc = ginit

        globs = self._program.globals()
        for G in globs:
            # bind the global to the state
            self.bot_state.memory.allocate_global(G, zeroed=G.is_zeroed())

            if not G.has_init():
                continue
            for i in G.init():
                # Hack for concurrent program: FIXME
                if self.get_options().threads:
                    ret = self._executor.execute_single_thread(self.bot_state, i)
                else:
                    ret = self._executor.execute(self.bot_state, i)
                assert len(ret) == 1, "Unhandled initialization"
                # assert ret[0] is s, "Unhandled initialization instruction"
                assert ret[
                    0
                ].is_ready(), (
                    "Generated errorneous state during initialization of globals"
                )

    def run(self) -> int:
        self.prepare()
        self.bot_state: TSEState = self.initial_states()
        self.bot_state.makeBottom()
        self.config = Configuration(self.bot_state)
        self.avoiding_set: set[TSEState] = {}
        self.adjoining_set: set[TSEState] = {}
        self.explore()

    def explore(self) -> None:
        """DFS exploring and creating possible configurations."""
        if self.config.enabled_events == {}:
            return
        if self.adjoining_set != {}:
            event = self.adjoining_set.intersection(self.config.enabled_events).pop()
        else:
            event = self.config.enabled_events.pop()

        data_race_result = self.config.add_event(event)
        if data_race_result:
            print("*********** DATA RACE DETECTED ***********")
            exit()
        self.adjoining_set.discard(event)
        self.explore()
        if event.conflicts != {}:
            self.config.remove_event(event)
            self.avoiding_set.add(event)
            self.adjoining_set = self.adjoining_set.union(event.conflicts)
            self.explore()

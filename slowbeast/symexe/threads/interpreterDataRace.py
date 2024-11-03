from typing import List, Set
from slowbeast.symexe.options import SEOptions
from slowbeast.symexe.threads.configuration import Configuration
from slowbeast.symexe.threads.iexecutor import IExecutor
from slowbeast.symexe.threads.interpreter import SymbolicInterpreter
from slowbeast.symexe.threads.state import TSEState


class PORSymbolicInterpreter(SymbolicInterpreter):

    def __init__(self, P, ohandler=None, opts: SEOptions = SEOptions()) -> None:
        print("Initiating the UPOR executor")
        super().__init__(P, ohandler, opts, IExecutor())
    
    def initial_states(self) -> TSEState:
        mem = self.executor.get_memory_model().create_memory()
        return TSEState(self.executor, None, mem, self.executor.solver)

    def run(self) -> int:
        self.prepare()
        self.bot_state : TSEState = self.initial_states()
        self.bot_state.makeBottom()
        self.config = Configuration(self.bot_state)
        self.avoiding_set : Set[TSEState] = {}
        self.adjoining_set : Set[TSEState] = {}
        self.explore()
    
    def explore(self) -> None:
        """ DFS exploring and creating possible configurations."""
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
        
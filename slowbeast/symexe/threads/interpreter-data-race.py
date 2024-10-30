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
        return self._executor.create_state()

    def run(self) -> int:
        self.prepare()
        self.bot_state : TSEState = self.initial_states()[0]
        self.bot_state.makeBottom()
        self.config = Configuration(self.bot_state)
        self.avoiding_set : Set[TSEState] = {}
        self.adjoining_set : Set[TSEState] = {}
        # Om Shree Ganeshay Namah!
        self.explore()
    
    def explore(self) -> None:
        """ DFS exploring and creating possible configurations."""
        if self.config.enabled_events == {}:
            return
        if self.adjoining_set != {}:
            event = self.adjoining_set.intersection(self.config.enabled_events).pop()
        else:
            event = self.config.enabled_events.pop()
        
        self.config.add_event(event)
        self.adjoining_set.discard(event)
        self.explore()
        if event.conflicts != {}:
            # FIXME it doesn't work if you change the configuration. You need to send
            # CUe without changing C.
            self.config.events.remove(event) # FIXME remove_event
            self.avoiding_set.add(event)
        # if there exists an alternative J : explore (C, DUe, J\C)
        
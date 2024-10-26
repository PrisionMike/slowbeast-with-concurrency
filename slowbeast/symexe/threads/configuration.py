from typing import List, Optional, Set

from slowbeast.symexe.threads.state import TSEState


class Configuration:
    """ Conflict free causally complete (linearly ordered) set of events (states)"""
    
    def __init__(self, bottom_event : Optional[TSEState] = None):
        self.events : Set[TSEState] = []
        self.extended_events : Set[TSEState] = set()
        self.enabled_events : Set[TSEState] = set()
        self.conflicting_extension : Set[TSEState] = set()
        self.bottom_event = bottom_event
        self.max_event : Optional[TSEState] = bottom_event
        if self.bottom_event != None:
            self.events.append(self.bottom_event)
    
    def add_event(self, event: TSEState):
        assert event in self.enabled_events, "Can't add non-enabled event"
        assert event.caused_by == self.max_event, "Has to be a LINEAR configuration"
        self.events.append(event)
        self.max_event = event
    
    def remove_event(self, event: TSEState):
        assert event in self.events, "Removing event not in configuration"
        stop_traversal : bool = False
        while self.max_event:
            if self.max_event.is_bot or stop_traversal:
                break
            if event == self.max_event:
                stop_traversal = True
            self.max_event = self.max_event.caused_by
            self.events.pop(event)


    
class Unfolding(Configuration):
    """ Causally complete partially ordered set of events, along with their conflict relations."""
    def __init__(self):
        pass

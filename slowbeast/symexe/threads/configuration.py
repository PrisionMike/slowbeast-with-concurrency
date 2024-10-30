from enum import Enum
from itertools import combinations
from typing import List, Optional, Set, Type

from slowbeast.ir.instruction import Call, Instruction, Load, Store
from slowbeast.symexe.threads.state import TSEState


class Configuration:
    """ Conflict free causally complete (linearly ordered) set of events (states)"""
    
    def __init__(self, bottom_event : Optional[TSEState] = None):
        self.events : Set[TSEState] = Set()
        # self.extended_events : Set[TSEState] = Set()
        self.enabled_events : Set[TSEState] = Set()
        self.conflicting_extension : Set[TSEState] = Set()
        self.bottom_event = bottom_event
        self.max_event : Optional[TSEState] = bottom_event
        if self.bottom_event is not None:
            self.events.add(self.bottom_event)
    
    def add_event(self, event: TSEState) -> bool:
        """ Adds event to configuration. Returns False if data race is detected."""
        assert event in self.enabled_events, "Can't add non-enabled event"
        self.events.add(event)
        self.max_event = event
        self.enabled_events = event.exec()
        map( draw_immediate_conflicts, combinations(self.enabled_events,2) )
        return not event.data_race
    
    # def exec(self) -> None:
    #     self.max_event.exec()
    # def remove_event(self, event: TSEState):
    #     """Likely unused"""
    #     assert event in self.events, "Removing event not in configuration"
    #     stop_traversal : bool = False
    #     while self.max_event:
    #         if self.max_event.is_bot or stop_traversal:
    #             break
    #         if event == self.max_event:
    #             stop_traversal = True
    #         self.max_event = self.max_event.caused_by
    #         self.events.remove(event)

def draw_immediate_conflicts( e1 : TSEState, e2 : TSEState) -> None:
    """ TODO 'Immediate' parameterisation no longer required I think. Do check."""
    assert e1.caused_by == e2.caused_by, "Can't have immediate conflict without a common parent"
    if e1.transition.thread_id == e2.transition.thread_id:
        add_immediate_conflict(e1, e2)
    else:
        i1 : Instruction = e1.transition.action
        i2 : Instruction = e2.transition.action
        r1 : Commutativity = are_commutative(i1, i2)
        r2 : Commutativity = are_commutative(i2, i1)
        if r1.result or r2.result:
            if r1.data_race or r2.data_race:
                e1.caused_by.data_race = True
            add_immediate_conflict(e1, e2)
    return

def add_immediate_conflict(e1 : TSEState, e2 : TSEState) -> None:
    """Makes sure both immediate and inherited conflicts are updated."""
    e1.conflicts.add(e2)
    e2.conflicts.add(e1)
    e2.immediate_conflicts.add(e1)
    e1.immediate_conflicts.add(e2)

class Commutativity:
    def __init__(self, commutes : bool, data_race : bool) -> None:
        self.result = commutes
        self.data_race = data_race

def are_commutative( i1 : Instruction, i2 : Instruction) -> Commutativity:
    if lock_check(i1, i2):
        return Commutativity(True, False)
    elif data_race_check(i1, i2):
        return Commutativity(True, True)

def lock_check( i1: Instruction, i2 : Instruction) -> bool:
    return (
        Type(i1) == Call and i1.called_function() == 'pthread_mutex_lock' and
        Type(i2) == Call and i2.called_function() == 'pthread_mutex_unlock' and
        i1.operand(0) == i2.operand(0)
    )

def data_race_check( i1: Instruction, i2 : Instruction) -> bool:
    return (
        Type(i1) == Load and
        Type(i2) == Store and
        i1.pointer_operand() == i2.pointer_operand()
    )

# class Unfolding(Configuration):
#     """ Causally complete partially ordered set of events, along with their conflict relations."""
#     def __init__(self, bottom_event : Optional[TSEState] = None):
#         super.__init__(bottom_event)
    
#     def add_events(self, extension_set : Set[TSEState] ) -> None:
#         if not extension_set:
#             return
#         else:
#             event = extension_set.pop()
#             parent_event = event.caused_by
#             extension_set.add(event)
#             for e in extension_set:
#                 parent_event.causes.add(e)
                
    

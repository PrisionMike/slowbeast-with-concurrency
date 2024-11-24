from __future__ import annotations

from copy import deepcopy
from slowbeast.ir.instruction import Instruction
from slowbeast.ir.instruction import Store, Load, Call


class Action:
    def __init__(self, tid: int | None, instr: Instruction | None):
        self.tid = tid
        self.instr = instr
        self.occurrence: int | None = None
        self.causes: set(Self) = set()
        self.caused_by: set(Self) = set()


class Trace:
    def __init__(self, sequence: list[Action] = []):
        self._sequence = sequence
        self._racist: set[Action] = set()  # actions in race with the last action
        self._backtrack: list[set[int] | None] = [set()]

    def append(self, e: Action) -> Self:
        """RETURNS an appended trace. Doesn't mutate instance."""
        new_trace = deepcopy(self)
        new_trace.set_occurrence(e)
        new_trace._sequence.append(e)
        new_trace._backtrack.append(None)
        new_trace.update_race_and_causality()
        return new_trace

    def set_backtrack(self, bt: set[int]) -> None:
        """sets backtrack"""
        self._backtrack[-1] = bt

    def get_racist_set(self):
        return self._racist

    def get_backtrack(self, action: Action | None = None) -> set(int):
        """Returns backtrack for the last action
        (= current trace) or backtrack of the PREFIX
        of the requested action"""
        if action is None:
            return self._backtrack[-1]
        return self._backtrack[self._sequence.index(action) - 1]

    def set_occurrence(self, act: Action) -> None:  # ✅
        for e in reversed(self._sequence):
            if e.tid == act.tid:
                act.occurrence = e.occurrence + 1
                break
        if act.occurrence is None:
            act.occurrence = 1

    def add_to_prefix_backtrack(self, action: Action, thread: int) -> None:  # ✅
        self._backtrack[self._sequence.index(action) - 1].add(thread)

    def independent_suffix_set(self, action: Action) -> set(int):  # ✅
        """The I_{E'.e}(notdep(e,E).p) for e."""
        isfset = set()
        initial_index = self._sequence.index(action) + 1
        initial_set = set(self._sequence[initial_index:])
        suffix_set = initial_set.difference(action.causes)
        suffix_set.add(self._sequence[-1])
        for e in suffix_set:
            if not e.caused_by.intersection(suffix_set):
                isfset.add(e.tid)
        return isfset

    def update_race_and_causality(self) -> None:  # ✅
        """Updates causal relation and racist set"""
        p = self._sequence[-1]
        for e in reversed(self._sequence[:-1]):
            if e.tid == p.tid:
                self.set_happens_before(e, p)
            elif self.in_data_race(e, p) or self.in_lock_race(e, p):
                self.set_happens_before(e, p)
                self._racist.add(e)

    def depends_on_last(self, q: Action) -> bool:
        p = self._sequence[-1]
        if p.tid == q.tid:
            return True
        else:
            return self.in_data_race(p, q) or self.in_lock_race(p, q)

    def in_data_race(self, e: Action, p: Action) -> bool:  # ✅
        instr1 = e.instr
        instr2 = p.instr
        if isinstance(instr1, Store) or isinstance(instr2, Store):
            store_instr, load_instr = (
                (instr1, instr2) if isinstance(instr1, Store) else (instr2, instr1)
            )
            if isinstance(load_instr, Load) or isinstance(load_instr, Store):
                return load_instr.pointer_operand() == store_instr.pointer_operand()
        return False

    def in_lock_race(self, e: Action, p: Action) -> bool:  # ✅
        return (
            isinstance(e.instr, Call)
            and isinstance(p.instr, Call)
            and e.instr.called_function() == "pthread_mutex_lock"
            and p.instr.called_function() == "pthread_mutex_lock"
            and e.instr.operand(0) == p.instr.operand(0)
        )

    def set_happens_before(self, e: Action, p: Action) -> None:  # ✅
        """Order matters"""
        e.causes.add(p)
        p.caused_by.add(e)

    def terminal_thread(self) -> int:
        return self._sequence[-1].tid

from typing import (
    Self,
    Set
)
from copy import deepcopy
from slowbeast.ir.instruction import Instruction
from slowbeast.ir.instruction import Store, Load, Call, Thread, ThreadJoin, Return
# from slowbeast.ir.types import PointerType


class Action:
    def __init__(self, tid: int | None, instr: Instruction | None):
        self.tid = tid
        self.occurrence: int | None = None
        self.occurrence: int | None = None
        self.causes: Set[Self] = set()
        self.caused_by: Set[Self] = set()
        self.instr = instr


class Trace:
    def __init__(self, sequence: list[Action] = []):
        self._sequence = sequence
        self._racist: list[set[Action] | None] = [
            set()
        ]  # actions in race with the last action
        # self._penultimate_racist: set[Action] = set() # Used for trimming the trace.
        self._backtrack: list[set[int] | None] = [set()]
        self.data_race = False

    def append(self, e: Action) -> Self:
        """RETURNS an appended trace. Doesn't mutate instance."""
        new_trace = deepcopy(self)
        new_trace.set_occurrence(e)
        new_trace._sequence.append(e)
        new_trace._backtrack.append(None)
        new_trace.update_race_and_causality()
        return new_trace

    def append_in_place(self, e: Action) -> None:
        """Appends the trace along with updating races and causality"""
        self.set_occurrence(e)
        self._sequence.append(e)
        self._backtrack.append(None)
        self._racist.append(set())
        self.update_race_and_causality()

    def trim(self) -> None:
        """Trims last event out of the trace. Preserves backtrack updates."""
        for e in self._sequence[-1].caused_by:
            e.causes.remove(self._sequence[-1])
        self._racist = self._racist[:-1]
        self._sequence = self._sequence[:-1]
        self._backtrack = self._backtrack[:-1]

    def set_backtrack(self, bt: set[int]) -> None:
        """sets backtrack"""
        self._backtrack[-1] = bt

    def get_racist_set(self):
        return self._racist[-1]

    def get_backtrack(self, action: Action | None = None) -> Set[int]:
        """Returns backtrack for the last action
        (= current trace) or backtrack of the PREFIX
        of the requested action"""
        backtrack = self._backtrack[-1]
        if action is None:
            backtrack = self._backtrack[-1]
        else:
            backtrack = self._backtrack[self._sequence.index(action)]
        assert backtrack is not None, "Backtrack should not be None"
        return backtrack

    def set_occurrence(self, act: Action) -> None:
        for e in reversed(self._sequence):
            assert e.occurrence is not None, "Unknown behaviour"
            if e.tid == act.tid:
                act.occurrence = e.occurrence + 1
                break
        if act.occurrence is None:
            act.occurrence = 1

    def add_to_prefix_backtrack(self, action: Action, thread: int) -> None:
        # Remove try-except block. Likely just needs None handling.
        try:
            self._backtrack[self._sequence.index(action)].add(thread) # type: ignore
        except ValueError:
            self._backtrack[self.index(action)].add(thread) # type: ignore

    def independent_suffix_set(self, action: Action) -> Set[int]:  # ✅
        """The I_{E'.e}(notdep(e,E).p) for e."""
        isfset: Set[int] = set()
        initial_index = self._sequence.index(action) + 1
        initial_set = set(self._sequence[initial_index:])
        e_causes = self.get_causes(action)
        e_caused_by = self.get_caused_by(action)
        suffix_set = initial_set.difference(e_causes)
        suffix_set.add(self._sequence[-1])
        for e in suffix_set:
            if not e_caused_by.intersection(suffix_set):
                # print(e)
                assert e.tid is not None, "Unknown behaviour"
                isfset.add(e.tid)
        return isfset

    def get_causes(self, e: Action) -> Set[Action]:
        """Returns transivitively closed set of causal successors"""
        successors : Set[Action] = set()

        stack = [e]
        while stack:
            current = stack.pop()
            for succ in current.causes:
                if succ not in successors:
                    successors.add(succ)
                    stack.append(succ)

        return successors

    def get_caused_by(self, e: Action) -> Set[Action]:
        """Returns transivitively closed set of causal predecessors"""
        predecessors: Set[Action] = set()

        stack = [e]
        while stack:
            current = stack.pop()
            for pred in current.caused_by:
                if pred not in predecessors:
                    predecessors.add(pred)
                    stack.append(pred)

        return predecessors

    def update_race_and_causality(self) -> None:  # ✅
        """Updates immediate causal relation and racist set"""
        p = self._sequence[-1]
        for e in reversed(self._sequence[:-1]):
            if e.tid == p.tid:
                if e.occurrence + 1 == p.occurrence:    # type: ignore
                    self.set_happens_before(e, p)
            elif self.in_data_race(e, p):
                if self.update_race(e, p):
                    self.data_race = True
                    break  # Should not break if data race detection is not the only goal.
                self.set_happens_before(e, p)
            elif self.in_lock_race(e, p):
                self.update_race(e, p)
                self.set_happens_before(e, p)
            elif self.non_reversible_causality(e, p):
                self.set_happens_before(e, p)

    def update_race(self, e: Action, p: Action) -> bool:
        """Returns True if race is updated"""
        e_causes = self.get_causes(e)
        if p not in e_causes:
            assert self._racist[-1] is not None, "Racist set should not be None"
            self._racist[-1].add(e)
            return True
        else:
            return False

    def non_reversible_causality(self, e: Action, p: Action) -> bool:
        """Order sensitive.
        Won't be added in race as reversed action sequence not possible."""
        return (
            self.unlock_causality(e, p)
            or self.fork_causality(e, p)
            or self.join_causality(e, p)
        )

    def unlock_causality(self, e: Action, p: Action) -> bool:
        """NOTE: Unlock "happens before" the NEXT instruction after Lock.
        Lock instructions are enabled regardless of lock being acquired.
        Instructions ahead are paused untill lock is acquired, ergo they
        relate to the unlock event.
        CHECK LOCK SUCCESS."""
        assert p.occurrence is not None, "Unknown behaviour"
        if (
            isinstance(e.instr, Call)
            and e.instr.called_function().name() == "pthread_mutex_unlock"  # type: ignore (legacy)
        ):
            for j in reversed(self._sequence):
                assert j.occurrence is not None, "Unknown behaviour"
                if (
                    j.tid == p.tid
                    and j.occurrence + 1 == p.occurrence
                    and isinstance(j.instr, Call)
                    and j.instr.called_function().name() == "pthread_mutex_lock" # type: ignore (legacy)
                    and j.instr.succ
                    and e.instr.operand(0) == j.instr.operand(0) # type: ignore (legacy)
                ):
                    return True
                if j.tid == p.tid and j.occurrence < p.occurrence - 1:
                    break
        return False

    def fork_causality(self, e: Action, p: Action) -> bool:
        if isinstance(e.instr, Thread):
            if e.instr.get_operand_tid() == p.tid and p.occurrence == 1:
                return True
        return False

    def join_causality(self, e: Action, p: Action) -> bool:
        assert p.occurrence is not None, "Unknown behaviour"
        if isinstance(e.instr, Return):
            for j in reversed(self._sequence):
                assert j.occurrence is not None, "Unknown behaviour"
                if (
                    j.tid == p.tid
                    and j.occurrence == p.occurrence - 1
                    and isinstance(j.instr, ThreadJoin)
                    and j.instr.get_operand_tid() == e.tid
                ):
                    return True
        return False

    def in_data_race(self, e: Action, p: Action) -> bool:
        instr1 = e.instr
        instr2 = p.instr
        if isinstance(instr1, Store) or isinstance(instr2, Store):
            store_instr, load_instr = (
                (instr1, instr2) if isinstance(instr1, Store) else (instr2, instr1)
            )
            if isinstance(load_instr, Load) or isinstance(load_instr, Store):
                return self.points_to_same_location(store_instr, load_instr) # type: ignore TODO
        return False

    def points_to_same_location(self, store_instr: Store, load_instr: Load) -> bool:
        """Checks if store and load point to the same location"""
        load_pointer_operand = load_instr.pointer_operand() # type: ignore
        store_pointer_operand = store_instr.pointer_operand() # type: ignore

        load_location = self.resolve_multi_pointers(load_pointer_operand) # type: ignore
        store_location = self.resolve_multi_pointers(store_pointer_operand) # type: ignore

        load_metadata = load_instr._metadata # type: ignore
        store_metadata = store_instr._metadata # type: ignore
        # lline = self.get_line_no_from_metadata(load_metadata) # type: ignore
        # sline = self.get_line_no_from_metadata(store_metadata) # type: ignore
        return load_location == store_location # type: ignore

    def resolve_multi_pointers(self, pointer_op): # type: ignore
        """Resolves double (or more) pointers"""
        return_op = pointer_op # type: ignore
        while isinstance(return_op, Load):
            return_op = return_op.pointer_operand() # type: ignore
        return return_op # type: ignore

    # def get_line_no_from_metadata(self, metadata: list):
    #     try:
    #         result = metadata[-1][-1][1]
    #     except IndexError:
    #         result = metadata
    #     return result

    def in_lock_race(self, e: Action, p: Action) -> bool:  # ✅
        return (
            isinstance(e.instr, Call)
            and isinstance(p.instr, Call)
            and e.instr.called_function().name() == "pthread_mutex_lock" # type: ignore (legacy)
            and p.instr.called_function().name() == "pthread_mutex_lock" # type: ignore (legacy)
            and e.instr.operand(0) == p.instr.operand(0) # type: ignore (legacy)
            and e.instr.succ  # LOCK ACQUIRED SUCCESSFULLY.
            and p.instr.succ  # LOCK ACQUIRED SUCCESSFULLY.
        )

    def set_happens_before(self, e: Action, p: Action) -> None:  # ✅
        """Order matters"""
        e.causes.add(p)
        p.caused_by.add(e)

    def terminal_thread(self) -> int:
        assert self._sequence[-1].tid is not None, "Unknown behaviour"
        return self._sequence[-1].tid

    def __len__(self):
        return len(self._sequence)

    def index(self, action: Action) -> int | None:
        ind = 0
        for e in self._sequence:
            if e.tid == action.tid and e.occurrence == action.occurrence:
                return ind
            else:
                ind += 1
        return None

    def depends_on_last(self, e: Action) -> bool:
        p = self._sequence[-1]
        # self.set_occurrence(e)
        assert p.tid != e.tid, "Actions from the same thread."
        return (
            self.in_data_race(e, p)
            or self.in_lock_race(e, p)
            or self.unlock_causality(e, p)
            or self.fork_causality(e, p)
            or self.join_causality(e, p)
        )

class Action:
    def __init__(self, tid: int | None = None, instr: Instruction | None = None):
        self.tid = tid
        self.instr = instr
        self.causes: set(Self) = set()
        self.caused_by: set(Self) = set()


class Trace:
    def __init__(self, sequence: list[Action] = []):
        self.sequence = sequence
        self.racist = set()  # actions in race with the last action
        self.backtrack: set(int) = set()

    def append(self, e: Action):
        self.sequence.append(e)
        self.update_causality()

    def happens_before_i(self, e1: Action, e2: Action) -> bool:
        assert e1 in self.sequence, "{e1} not in current execution trace"
        assert e2 in self.sequence, "{e2} not in current execution trace"
        i1 = self.sequence.index(e1)
        i2 = self.sequence.index(e2)
        if e1.tid == e2.tid:
            return i1 < i2
        else:
            # TODO
            # return lock_check(e1, e2) or data_race_check(e1, e2)
            pass

    def prefix(self, e: Action) -> Self:
        return Trace(self.sequence[: self.sequence.index(e)])

    def preceding_action(self, e: Action) -> Action:
        return self.sequence[self.sequence.index(e) - 1]

    def suffix_indep(self, e: Action) -> Self:
        assert e in self.sequence

    def godfathers(self, prefix: list[Action], w: list[Action]) -> set(Action):
        assert self.sequence[: len(prefix)] == prefix

    def reversible_race(self, e1: Action, e2: Action) -> bool:
        if e1.tid == e2.tid:
            return True
        else:
            return self.happens_before_i(e1, e2)

    def update_causality(self) -> None:
        """Updates causal relation and racist set"""
        pass

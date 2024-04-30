from slowbeast.core.state import ExecutionState
from slowbeast.symexe.memory import Memory

class ConcurrentState(ExecutionState):
    def __init__(self, pc: None = None, m: Memory | None = None) -> None:
        super().__init__(pc, m)
from slowbeast.core.memory import Memory as CoreMemory
from slowbeast.symexe.memoryobject import MemoryObject
from slowbeast.domains.concrete_bitvec import ConcreteBitVec
from typing import Optional


class Memory(CoreMemory):
    def create_memory_object(
        self,
        size: ConcreteBitVec,
        nm: Optional[str] = None,
        objid: None = None,
        is_global: bool = False,
    ) -> MemoryObject:
        """
        Create a new memory object -- may be overridden
        by child classes to create a different type of
        memory objects.
        """
        return MemoryObject(size, nm, objid, is_global)

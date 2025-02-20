from copy import copy
from sys import stdout

from slowbeast.ir.instruction import Branch
from slowbeast.analysis.cfg.CFG import Node
from typing import Sized, TextIO


class CFG:
    class Node:
        __slots__ = ["_cfg", "_block", "_successors", "_predecessors"]

        def __init__(self, cfg, B):
            self._cfg = cfg
            self._block = B
            self._successors = []
            self._predecessors = []

        def bblock(self):
            return self._block

        def successors(self):
            return self._successors

        def predecessors(self):
            return self._predecessors

        def add_successor(self, succ):
            for s in self._successors:
                if s == succ:
                    return

            self._successors.append(succ)
            succ._predecessors.append(self)

        def get_cfg(self):
            return self._cfg

        def is_join(self):
            "This bblock Has several predecessors"
            return len(self._predecessors) > 1

        def is_branch(self):
            "This bblock Has several successors"
            return len(self._successors) > 1

    def __init__(self, F) -> None:
        self._fun = F
        self._entry = None
        self._nodes = {}

        self._build()

    def fun(self):
        return self._fun

    def create_node(self, *args) -> Node:
        """Override this method in child classes
        to get nodes with more data
        """
        assert len(args) == 1
        return CFG.Node(self, *args)

    def get_node(self, B):
        return self._nodes.get(B)

    def get_nodes(self):
        return self._nodes.values()

    def entry(self):
        assert self._entry, "Entry has not been set"
        return self._entry

    def set_entry(self, n) -> None:
        if not isinstance(n, CFG.Node):
            n = self.get_node(n)

        assert hasattr(n, "successors")
        self._entry = n

    def _build(self) -> None:
        fun = self._fun

        for B in fun.bblocks():
            self._nodes[B] = self.create_node(B)

        for block, node in self._nodes.items():
            br = block.last()
            if not isinstance(br, Branch):
                continue

            node.add_successor(self._nodes[br.true_successor()])
            node.add_successor(self._nodes[br.false_successor()])

        # the entry should be the first bblock in the function
        entrybb = fun.bblock(0)
        assert self.get_node(entrybb)
        self.set_entry(entrybb)

    def dump(self, stream: TextIO = stdout) -> None:
        for node in self._nodes.values():
            for succ in node.successors():
                stream.write(f"{node.bblock().get_id()} -> {succ.bblock().get_id()}\n")


class CFGPath:
    def __init__(self, locs=None) -> None:
        if locs:
            assert isinstance(locs, list)
            assert all(map(lambda x: isinstance(x, CFG.Node), locs))
            self._locations = locs
        else:
            self._locations = []

    def __len__(self) -> int:
        return len(self._locations)

    def __getitem__(self, idx):
        assert idx < len(self._locations)
        return self._locations[idx]

    def __iter__(self):
        return self._locations.__iter__()

    def copy(self) -> "CFGPath":
        return copy(self)

    def subpath(self, start, end) -> None:
        n = copy(self)
        n._locations = self._locations[start:end]

    def append(self, l) -> None:
        self._locations.append(l)

    def first(self):
        if len(self._locations) == 0:
            return None
        return self._locations[0]

    def last(self):
        if len(self._locations) == 0:
            return None
        return self._locations[-1]

    def endswith(self, path: Sized) -> bool:
        if len(self) < len(path):
            return False

        if len(path) == 0:
            return True

        pl = len(path) - 1
        sl = len(self) - 1
        for idx in range(0, len(path)):
            if path._locations[pl - idx] != self._locations[sl - idx]:
                return False
        return True

    def locations(self):
        return self._locations

    def length(self) -> int:
        return len(self._locations)

    def dump(self, stream: TextIO = stdout) -> None:
        stream.write(str(self))
        stream.write("\n")

    def __repr__(self) -> str:
        return " -> ".join(map(lambda x: str(x.bblock().get_id()), self._locations))

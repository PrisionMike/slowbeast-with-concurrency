from sys import stdout
from typing import TextIO

from slowbeast.ir.function import Function
from slowbeast.ir.instruction import Call
from slowbeast.util.debugging import FIXME


class CallGraph:
    class Node:
        __slots__ = "_fun", "_callsites", "_callers"

        def __init__(self, F):
            self._fun = F
            self._callers = []
            self._callsites = {}

        def fun(self):
            return self._fun

        def callsites(self):
            return self._callsites

        def callers(self):
            return self._callers

        def add_callsite(self, callsite, funs):
            """
            This node contains a call-site 'callsite'
            that calls funs
            """
            self._callsites[callsite] = funs
            for f in funs:
                f._callers.append((self, callsite))

        def predecessors(self):
            """
            Simple predecessors (over functios)
            """
            return (f for (f, cs) in self._callers)

        def successors(self):
            """
            Simple successors (over functios)
            """
            return set(
                (v for funs in self._callsites.values() for v in funs)
            ).__iter__()

    __slots__ = "_program", "_nodes"

    def __init__(self, P) -> None:
        self._program = P
        self._nodes = {}

        self._build()

    def create_node(self, *args) -> Node:
        """Override this method in child classes
        to get nodes with more data
        """
        assert len(args) == 1
        return CallGraph.Node(*args)

    def get_node(self, B):
        return self._nodes.get(B)

    def get_nodes(self):
        return self._nodes.values()

    def funs(self):
        return (f.fun() for f in self._nodes.values())

    def _build(self) -> None:
        for F in self._program.funs():
            self._nodes[F] = self.create_node(F)

        for _fun, node in self._nodes.items():
            self._build_fun(_fun, node)

    def _build_fun(self, _fun, node) -> None:
        for block in _fun.bblocks():
            for I in block.instructions():
                if not isinstance(I, Call):
                    continue

                # this function (node) contains call I that calls ...
                cf = I.called_function()
                called_node = self._nodes.get(cf)
                if called_node:
                    node.add_callsite(I, [called_node])
                else:
                    FIXME(f"Ignoring function pointer call: {I}")

    def get_reachable(self, node: Node):
        if isinstance(node, Function):
            node = self.get_node(node)
        assert isinstance(node, CallGraph.Node)

        queue = [node]
        reachable = set()
        while queue:
            n = queue.pop()
            reachable.add(n)
            for s in n.successors():
                if s not in reachable:
                    queue.append(s)

        return reachable

    def prune_unreachable(self, frm: Node) -> None:
        reach = self.get_reachable(frm)
        nonreach = [(k, n) for (k, n) in self._nodes.items() if n not in reach]
        for k, n in nonreach:
            self._nodes.pop(k)

    def dump(self, stream: TextIO = stdout) -> None:
        for f, node in self._nodes.items():
            stream.write(f"Fun '{f.name()}' calls\n")
            for cs, funs in node.callsites().items():
                for n, cf in enumerate(funs):
                    if n == 0:
                        stream.write(f"  {cs.get_id()} -> {cf.fun().name()}\n")
                    else:
                        stream.write(f"     -> {cf.fun().name()}\n")

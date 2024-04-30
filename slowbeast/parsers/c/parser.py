try:
    import clang.cindex
    clang.cindex.Config.set_library_file('/usr/lib/x86_64-linux-gnu/libclang-14.so.14.0.0')
except ImportError as e:
    raise ImportError(f"Need clang bindings: {e}")

from slowbeast.domains.concrete_bitvec import ConcreteBitVec
from slowbeast.domains.concrete_value import ConcreteVal
from slowbeast.ir.function import Function
from slowbeast.ir.instruction import *
from slowbeast.ir.program import Program
from slowbeast.ir.types import *
from typing import Optional


class Parser:
    def __init__(self) -> None:
        self.program = Program()
        self._bblocks = {}
        self._mapping = {}
        self._funs = {}
        self._metadata_opts = ["c"]
        self._tus = {}

    def fun(self, fn: str) -> Optional[Function]:
        return self.program.fun(fn)

    def _add_mapping(self, celem, sbinst) -> None:
        if "c" in self._metadata_opts:
            sbinst.add_metadata("c", str(celem))
        assert self._mapping.get(ccode) is None, "Duplicated mapping"
        self._mapping[celem] = sbinst

    def parse(self, code) -> None:
        print(f"Parse {code}")
        index = clang.cindex.Index.create()
        tus = self._tus
        for cfile in code:
            tu = index.parse(cfile)
            print("Translation unit:", tu.spelling)
            tus[cfile] = tu
            print("tu.cursor.kind: ", tu.cursor.kind)
            print("tu.cursor.spelling: ",tu.cursor.spelling)
            print("tu.cursor.location: ",tu.cursor.location)
            for c in tu.cursor.get_children():
                try:
                    print("c.kind:  ", c.kind)
                    print("c.spelling:  ", c.spelling)
                    print("c.location:  ", c.location)
                    print("c.is_definition():  ", c.is_definition())
                except e:
                    print(str(e))

            # succ, retty = parse_fun_ret_ty(self.llvmmodule, f.type.element_type)
            # if not succ:
            #    raise NotImplementedError(
            #        "Cannot parse function return type: {0}".format(f.type.element_type)
            #    )
            # self.program.add_fun(Function(f.spelling, len(list(f.arguments)), retty))

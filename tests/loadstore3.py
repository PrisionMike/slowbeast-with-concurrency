import sys
from os.path import join, abspath, dirname
pth = join(dirname(__file__), '..')
sys.path.append(abspath(pth))

from slowbeast.ir.program import *
from slowbeast.ir.bblock import *
from slowbeast.ir.instruction import *
from slowbeast.ir.function import *

from slowbeast.interpreter.interpreter import *

if __name__ == "__main__":
    P = Program()
    F = Function("main")

    B0 = BBlock(F)

    A = Alloc(Constant(4, 4))
    Ptr = Alloc(Constant(8, 4))
    B0.append(A)
    B0.append(Ptr)
    B0.append(Store(Constant(123, 4), A))
    B0.append(Store(A, Ptr))
    L1 = Load(Ptr, 8)
    L2 = Load(L1, 4)
    B0.append(L1)
    B0.append(L2)
    B0.append(Print(Constant("Loaded: ", 8), L2))
    C2 = Cmp(Cmp.EQ, L2, Constant(123, 4))
    B0.append(C2)
    B0.append(Assert(C2))
    B0.append(Return(Constant(0, 4)))

    P.addFun(F)
    P.setEntry(F)
    #P.dump()

    I = Interpreter(P)
    I.run()

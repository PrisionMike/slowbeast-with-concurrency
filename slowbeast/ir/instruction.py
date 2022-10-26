from sys import stdout
from typing import Sized, Union, TextIO

from slowbeast.ir.bblock import BBlock
from slowbeast.ir.types import PointerType, Type
from slowbeast.util.debugging import print_highlight
from .programelement import ProgramElement
from .types import LabelType, BitVecType, BoolType, get_offset_type


class GlobalVariable(ProgramElement):
    def __init__(self, size, name, const: bool = False) -> None:
        super().__init__()
        self._size = size
        self._name = name
        # is the pointed memory constant?
        self._isconst = const
        # sequence of instructions used to initialize this global
        self._init = []
        self._zeroed = False

    def is_global(self) -> bool:
        return True

    def type(self) -> PointerType:
        return PointerType()

    def size(self):
        return self._size

    def name(self):
        return self._name

    def has_init(self) -> bool:
        """
        Is this variable initialized? It is initialized if it has some associated init sequence
        or is zeroed. Note that it does not mean it is initialized entirely.
        """
        return self._init is not None or self._zeroed

    def set_name(self, nm) -> None:
        self._name = nm

    def set_zeroed(self) -> None:
        self.add_metadata("init", "zeroed")
        self._zeroed = True

    def is_zeroed(self) -> bool:
        return self._zeroed

    def init(self):
        return self._init

    def set_init(self, I) -> None:
        for i in I:
            self.add_metadata("init", str(i))
        self._init = I

    def as_value(self) -> str:
        return f"g{self.get_id()}"

    def __str__(self) -> str:
        return f"{self.as_value()} = global {self.name()} of size {self.size()}"

    def dump(self, ind: int = 0, stream: TextIO = stdout, color: bool = True) -> None:
        super().dump(ind, stream, color)
        stream.write(f"{' ' * ind}{self}\n")


class Instruction(ProgramElement):
    def __init__(self, ops=None, types=None) -> None:
        super().__init__()
        self._operands = ops or []
        self._op_types = types or []
        assert len(self._operands) == len(
            self._op_types
        ), "Each operand must have associated expected type!"

        self._bblock = None
        self._bblock_idx = None

    def operand(self, idx):
        assert idx < len(self._operands)
        return self._operands[idx]

    def operands(self):
        return self._operands

    def expected_op_types(self):
        return self._op_types

    def op_type(self, idx: int) -> Type:
        return self._op_types[idx]

    def operands_num(self) -> int:
        return len(self._operands)

    def set_bblock(self, bb, idx) -> None:
        assert bb, "None bblock is invalid"
        assert idx >= 0, "Invalid bblock idx"
        self._bblock = bb
        self._bblock_idx = idx

    def bblock(self):
        return self._bblock

    def fun(self):
        assert self._bblock
        return self._bblock.fun()

    def bblock_idx(self):
        return self._bblock_idx

    def dump(self, ind: int = 0, stream: TextIO = stdout, color: bool = True) -> None:
        super().dump(ind, stream)
        if color:
            print_highlight(
                str(self),
                {
                    "store": "WINE",
                    "load": "WINE",
                    "sext": "WINE",
                    "zext": "WINE",
                    "call": "WINE",
                    "assert": "WINE",
                    "assume": "WINE",
                    "branch": "WINE",
                    "ret": "WINE",
                    "cmp": "WINE",
                    "alloc": "WINE",
                    "cast": "WINE",
                    "bblock": "GREEN",
                },
                " " * ind,
                stream=stream,
            )
        else:
            stream.write(f"{' ' * ind}{self}\n")

    ###
    # Helper methods
    def insert_before(self, i):
        assert self.bblock() is None
        assert self.bblock_idx() is None
        assert i.bblock() is not None
        assert i.bblock_idx() is not None
        return i.bblock().insert(self, i.bblock_idx())

    def get_next_inst(self):
        assert self.bblock() is not None
        assert self.bblock_idx() is not None
        assert isinstance(self.bblock(), BBlock)
        return self.bblock().get_next_inst(self.bblock_idx())


class ValueInstruction(Instruction):
    """
    Instruction that generates a value
    """

    def __init__(self, ops=None, types=None) -> None:
        super().__init__(ops, types)
        self._name = None

    # def is_concrete(self) -> bool:
    #    return False

    def set_name(self, nm) -> None:
        self._name = nm

    def as_value(self) -> str:
        if self._name:
            return f"{self._name}"
        return f"x{self.get_id()}"


class ValueTypedInstruction(ValueInstruction):
    """
    ValueInstruction with associated type of the generated value
    """

    def __init__(self, valty, ops=None, types=None) -> None:
        super().__init__(ops, types)
        self._type = valty

    def type(self):
        return self._type


class Store(Instruction):
    """Store 'val' to 'to'"""

    def __init__(self, val, to, optypes: Sized) -> None:
        assert val, val
        assert to, to
        assert len(optypes) == 2, optypes
        super().__init__([val, to], optypes)

    def pointer_operand(self):
        return self.operand(1)

    def value_operand(self):
        return self.operand(0)

    def bytewidth(self) -> int:
        return self.operand(0).bytewidth()

    def bitwidth(self) -> int:
        return self.bytewidth() * 8

    def __str__(self) -> str:
        optypes = self.expected_op_types()
        return "store ({2}){0} to ({3}){1}".format(
            self.value_operand().as_value(),
            self.pointer_operand().as_value(),
            optypes[0],
            optypes[1],
        )


class Load(ValueTypedInstruction):
    """Load value of type 'ty' from 'frm'"""

    def __init__(
        self, frm: Union[GlobalVariable, Instruction], ty: Type, optypes: Sized
    ) -> None:
        assert isinstance(ty, Type), ty
        assert isinstance(frm, (Instruction, GlobalVariable)), frm
        assert len(optypes) == 1, optypes
        super().__init__(ty, [frm], optypes)

    def bytewidth(self):
        return self._type.bytewidth()

    def bitwidth(self):
        return self._type.bitwidth()

    def pointer_operand(self):
        return self.operand(0)

    def __str__(self) -> str:
        return "x{0}: {2} = load ({3}){1}".format(
            self.get_id(),
            self.pointer_operand().as_value(),
            self.type(),
            self.expected_op_types()[0],
        )


class Alloc(ValueInstruction):
    def __init__(self, size, on_heap: bool = False) -> None:
        assert isinstance(on_heap, bool), on_heap
        super().__init__()
        self._size = size
        self._is_heap = on_heap

    def size(self):
        return self._size

    def type(self) -> PointerType:
        return PointerType()

    def __str__(self) -> str:
        return "{0} = alloc {1} bytes{2}".format(
            self.as_value(),
            self.size().as_value(),
            " on heap" if self._is_heap else "",
        )

    # the allocations return pointers, we need to compare them
    def __lt__(self, other) -> bool:
        return self.get_id() < other.get_id()

    def __le__(self, other) -> bool:
        return self.get_id() <= other.get_id()

    def __gt__(self, other) -> bool:
        return self.get_id() > other.get_id()

    def __ge__(self, other) -> bool:
        return self.get_id() >= other.get_id()

    # must override the hash since we defined the operators
    # defined in super class
    # def __hash__(self):
    #    return self.get_id()


class Branch(Instruction):
    def __init__(self, cond, b1: BBlock, b2: BBlock) -> None:
        super().__init__([cond, b1, b2], [BoolType(), LabelType(), LabelType()])
        assert isinstance(b1, BBlock)
        assert isinstance(b2, BBlock)

    def condition(self):
        return self.operand(0)

    def true_successor(self):
        return self.operand(1)

    def false_successor(self):
        return self.operand(2)

    def __str__(self) -> str:
        return "branch {0} ? {1} : {2}".format(
            self.condition().as_value(),
            self.true_successor().as_value(),
            self.false_successor().as_value(),
        )


class Switch(Instruction):
    def __init__(self, val, default: BBlock, cases: list) -> None:
        super().__init__([val, default] + cases)
        assert isinstance(default, BBlock), default
        assert isinstance(cases, list), cases
        assert all(map(lambda p: p[0].type().is_bv(), cases)), cases
        assert all(map(lambda p: isinstance(p[1], BBlock), cases)), cases

    def condition(self):
        return self.operand(0)

    def default_bblock(self):
        return self.operand(1)

    def cases(self):
        return self.operands()[2:]

    def __str__(self) -> str:
        return (
            "switch on {0}:\n  {1}".format(
                self.condition().as_value(),
                "\n  ".join(
                    f"{v.as_value() : >7} -> {c.as_value()}" for (v, c) in self.cases()
                ),
            )
            + f"\n  default -> {self.default_bblock().as_value()}"
        )


class Call(ValueTypedInstruction):
    def __init__(self, wht, ty, operands, optypes) -> None:
        super().__init__(ty, operands, optypes)
        self._function = wht

    def called_function(self):
        return self._function

    def function_type(self):
        assert self.type() == self._function.type()
        return self.type()

    def return_value(self):
        raise NotImplementedError("No return values in funs yet")
        # return self._function

    def __str__(self) -> str:
        if self.type() is None:
            r = f"call {self.called_function().as_value()}("
        else:
            r = f"x{self.get_id()}: {self.type()} = call {self.called_function().as_value()}("
        r += ", ".join(
            f"({ty}){x.as_value()}"
            for x, ty in zip(self.operands(), self.expected_op_types())
        )
        return r + ")"


class Return(Instruction):
    def __init__(self, val=None, rettype=None) -> None:
        if val is None:
            assert rettype is None
            super().__init__([])
        else:
            assert rettype is not None
            super().__init__([val], [rettype])

    def __str__(self) -> str:
        if len(self.operands()) == 0:
            return "ret"
        return f"ret ({self.expected_op_types()[0]}){str(self.operand(0).as_value())}"


class Thread(Call):
    def __init__(self, wht, *operands) -> None:
        super().__init__(wht, get_offset_type(), *operands)

    def called_function(self):
        return self._function

    def type(self):
        return self._function.type()

    def return_value(self):
        raise NotImplementedError("No return values in funs yet")
        # return self._function

    def __str__(self) -> str:
        r = f"x{self.get_id()} = thread {self.called_function().as_value()}("
        r += ", ".join(map(lambda x: x.as_value(), self.operands()))
        return r + f") -> {self._type}"


class ThreadExit(Return):
    def __init__(self, val=None) -> None:
        super().__init__(val)

    def __str__(self) -> str:
        if len(self.operands()) == 0:
            return "thread exit"
        return f"thread exit ret {self.operand(0).as_value()}"


class ThreadJoin(ValueTypedInstruction):
    def __init__(self, ty, ops=None) -> None:
        super().__init__(ty, ops)

    def __str__(self) -> str:
        if len(self.operands()) == 0:
            r = "thread join"
        else:
            r = f"x{self.get_id()} = thread join ("
        r += ", ".join(map(lambda x: x.as_value(), self.operands()))
        return r + ")"


class Print(Instruction):
    def __init__(self, *operands) -> None:
        super().__init__([*operands], [None] * len(operands))

    def __str__(self) -> str:
        r = "print "
        for o in self._operands:
            r += o.as_value() + " "
        return r


class Assert(Instruction):
    def __init__(self, cond, msg=None) -> None:
        super().__init__([cond, msg], [BoolType, None])

    def msg(self):
        ops = self.operands()
        assert len(ops) <= 2 and len(ops) >= 1
        if len(ops) == 1:
            return None
        return ops[1]

    def condition(self):
        return self.operand(0)

    def __str__(self) -> str:
        r = f"assert {self.condition().as_value()}"
        m = self.msg()
        if m:
            r += f', "{m}"'
        return r


class Assume(Instruction):
    def __init__(self, *operands) -> None:
        super().__init__([*operands], [BoolType] * len(operands))

    def __str__(self) -> str:
        r = "assume "
        for n, o in enumerate(self._operands):
            if n > 0:
                r += " && "
            r += o.as_value()
        return r


class Cmp(ValueTypedInstruction):
    LE = 1
    LT = 2
    GE = 3
    GT = 4
    EQ = 5
    NE = 6

    def predicate_str(p, u: bool = False) -> str:
        if p == Cmp.LE:
            s = "<="
        elif p == Cmp.LT:
            s = "<"
        elif p == Cmp.GE:
            s = ">="
        elif p == Cmp.GT:
            s = ">"
        elif p == Cmp.EQ:
            s = "=="
        elif p == Cmp.NE:
            s = "!="
        else:
            raise NotImplementedError("Invalid comparison")

        if u:
            s += "u"

        return s

    def predicate_neg(p) -> int:
        if p == Cmp.LE:
            return Cmp.GT
        if p == Cmp.LT:
            return Cmp.GE
        if p == Cmp.GE:
            return Cmp.LT
        if p == Cmp.GT:
            return Cmp.LE
        if p == Cmp.EQ:
            return Cmp.NE
        if p == Cmp.NE:
            return Cmp.EQ

        raise NotImplementedError("Invalid comparison")

    def __init__(self, p, val1, val2, types, unsgn_or_unord: bool = False) -> None:
        super().__init__(BoolType(), [val1, val2], types)
        self._predicate = p
        self._unsigned_or_unordered = unsgn_or_unord

    def set_unsigned(self) -> None:
        """Set that this comparison is unsigned"""
        self._unsigned_or_unordered = True

    def is_unsigned(self) -> bool:
        return self._unsigned_or_unordered

    set_unordered = set_unsigned
    is_unordered = is_unsigned

    def predicate(self):
        return self._predicate

    def __str__(self) -> str:
        ety = self.expected_op_types()
        return "{0}: {4} = cmp ({5}){1} {2} ({6}){3}".format(
            self.as_value(),
            self.operand(0).as_value(),
            Cmp.predicate_str(self.predicate(), self.is_unsigned()),
            self.operand(1).as_value(),
            self.type(),
            ety[0],
            ety[1],
        )


class UnaryOperation(ValueTypedInstruction):
    ABS = 1
    EXTEND = 2
    CAST = 3
    NEG = 4
    EXTRACT = 5
    FP_OP = 6

    def __init__(self, op, a, retty, optypes) -> None:
        assert retty is not None
        super().__init__(retty, [a], optypes)
        self._op = op

    def operation(self):
        return self._op


class Abs(UnaryOperation):
    """Absolute value"""

    def __init__(self, val, retty: Type, optypes: list) -> None:
        super().__init__(UnaryOperation.ABS, val, retty, optypes)

    def __str__(self) -> str:
        return f"x{self.get_id()}:{self.type()} = abs(({(self.expected_op_types()[0])}){self.operand(0).as_value()})"


class Extend(UnaryOperation):
    def __init__(self, a, bw: int, signed: bool, optypes) -> None:
        assert isinstance(bw, int), f"Invalid bitwidth to extend: {bw}"
        assert isinstance(signed, bool), f"Invalid signed flag: {bw}"
        super().__init__(UnaryOperation.EXTEND, a, BitVecType(bw), optypes)
        self._bw = bw
        self._signed = signed

    def bitwidth(self) -> int:
        return self._bw

    def is_signed(self) -> bool:
        return self._signed

    def __str__(self) -> str:
        return "x{0}: {3} = extend {5} ({4}){1} to {2} bits".format(
            self.get_id(),
            self.operand(0).as_value(),
            self.bitwidth(),
            self.type(),
            self.op_type(0),
            "signed" if self.is_signed() else "unsigned",
        )


class Cast(UnaryOperation):
    def __init__(self, a, ty: Type, sgn, optypes) -> None:
        assert isinstance(ty, Type)
        super().__init__(UnaryOperation.CAST, a, ty, optypes)
        self._signed = sgn

    def casttype(self):
        return self.type()

    def signed(self) -> bool:
        return self._signed

    def __str__(self) -> str:
        return "x{0}:{3} = cast ({4}){1} to {2}{3}".format(
            self.get_id(),
            self.operand(0).as_value(),
            "signed " if self._signed else "",
            self.casttype(),
            self.op_type(0),
        )


class Neg(UnaryOperation):
    """Negate the number (return the same number with opposite sign)"""

    def __init__(self, val, retty, optypes) -> None:
        super().__init__(UnaryOperation.NEG, val, retty, optypes)

    def __str__(self) -> str:
        return "x{0}:{2} = -(({3}){1})".format(
            self.get_id(), self.operand(0).as_value(), self.type(), self.op_type(0)
        )


class ExtractBits(UnaryOperation):
    def __init__(self, val, start, end, optypes) -> None:
        assert start.is_concrete(), "Invalid bitwidth to extend"
        assert end.is_concrete(), "Invalid bitwidth to extend"
        super().__init__(
            UnaryOperation.EXTRACT,
            val,
            BitVecType(end.value() - start.value() + 1),
            optypes,
        )
        self._start = start
        self._end = end

    def range(self):
        return (self._start, self._end)

    def start(self):
        return self._start

    def end(self):
        return self._end

    def __str__(self) -> str:
        return "x{0}:{4} = extractbits {1}-{2} from ({5}){3}".format(
            self.get_id(),
            self.start(),
            self.end(),
            self.operand(0).as_value(),
            self.type(),
            self.op_type(0),
        )


class FpOp(UnaryOperation):
    """Floating-point special operations"""

    IS_INF = 1
    IS_NAN = 2
    FPCLASSIFY = 3
    SIGNBIT = 4

    def op_to_str(op) -> str:
        if op == FpOp.IS_INF:
            return "isinf"
        if op == FpOp.IS_NAN:
            return "isnan"
        if op == FpOp.FPCLASSIFY:
            return "fpclassify"
        if op == FpOp.SIGNBIT:
            return "signbit"
        return "uknwn"

    def __init__(self, fp_op, val, valty) -> None:
        assert FpOp.IS_INF <= fp_op <= FpOp.SIGNBIT
        super().__init__(UnaryOperation.FP_OP, val, [valty])
        self._fp_op = fp_op

    def fp_operation(self):
        return self._fp_op

    def __str__(self) -> str:
        return "x{0} = fp {1} {2}".format(
            self.get_id(), FpOp.op_to_str(self._fp_op), self.operand(0).as_value()
        )


class BinaryOperation(ValueTypedInstruction):
    # arith
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    UDIV = 12
    REM = 11
    UREM = 13
    # bitwise
    SHL = 5
    LSHR = 6
    ASHR = 7
    # logical
    AND = 8
    OR = 9
    XOR = 10
    # more logicals to come ...
    LAST = 14

    def __init__(self, op, a, b, optypes) -> None:
        isptr = a.type().is_pointer() or b.type().is_pointer()
        assert isptr or a.type() == b.type(), f"{a} ({a.type()}), {b} ({b.type()})"
        assert BinaryOperation.ADD <= op <= BinaryOperation.LAST
        super().__init__(PointerType() if isptr else a.type(), [a, b], optypes)
        self._op = op

    def op_str(op) -> str:
        # arith
        if op == BinaryOperation.ADD:
            return "+"
        if op == BinaryOperation.SUB:
            return "-"
        if op == BinaryOperation.MUL:
            return "*"
        if op == BinaryOperation.DIV:
            return "/"
        if op == BinaryOperation.UDIV:
            return "u/"
        if op == BinaryOperation.REM:
            return "%"
        if op == BinaryOperation.UREM:
            return "u%"
        if op == BinaryOperation.SHL:
            return "<<"
        if op == BinaryOperation.LSHR:
            return "l>>"
        if op == BinaryOperation.ASHR:
            return ">>"
        if op == BinaryOperation.AND:
            return "&"
        if op == BinaryOperation.OR:
            return "|"
        if op == BinaryOperation.XOR:
            return "^"
        raise RuntimeError(f"Unknown binary op: {op}")

    def operation(self):
        return self._op

    def __str__(self) -> str:
        ety = self.expected_op_types()
        return "x{0}:{3} = ({4}){1} {6} ({5}){2}".format(
            self.get_id(),
            self.operand(0).as_value(),
            self.operand(1).as_value(),
            self.type(),
            ety[0],
            ety[1],
            BinaryOperation.op_str(self.operation()),
        )


# TODO: do we want this instruction? (can we replace it somehow without
# creating an artificial braching?).
class Ite(ValueTypedInstruction):
    """if-then-else: assign a value based on a condition"""

    def __init__(self, cond, op1, op2) -> None:
        assert cond.type().bitwidth() == 1
        assert op1.type() == op2.type(), "Invalid types in Ite"
        super().__init__(op1.type(), [op1, op2])
        self._cond = cond

    def condition(self):
        return self._cond

    def __repr__(self) -> str:
        return (
            f"{self.as_value()} = if {self._cond.as_value()} then "
            f"{self.operand(0).as_value()} else {self.operand(1).as_value()}"
        )

from struct import pack, unpack
from typing import Optional, Union

from numpy import float64

from slowbeast.domains.concrete_bitvec import ConcreteBitVec, to_signed
from slowbeast.domains.concrete_bool import ConcreteBoolDomain
from slowbeast.domains.concrete_floats import (
    ConcreteFloat,
    ConcreteFloatsDomain,
    concrete_float_val_to_bytes,
    float_to_bv,
)
from slowbeast.domains.concrete_value import ConcreteVal, ConcreteBool
from slowbeast.ir.types import Type
from .concrete_bitvec import (
    ConcreteBitVecDomain,
)
from .concrete_bytes import ConcreteBytes, ConcreteBytesDomain, int_to_bytes
from .domain import Domain
from .value import Value
from ..ir.instruction import IntOp


def to_fp(x, bw):
    val = x.value()
    if x.is_float():
        return val
    print(val)
    if val < 0:
        packed = pack("i", val) if x.bitwidth() == 32 else pack("l", val)
    else:
        packed = pack("I", val) if x.bitwidth() == 32 else pack("L", val)
    return (unpack("f", packed) if bw == 32 else unpack("d", packed))[0]


def get_any_domain(a: Value):
    if a.is_bv():
        return ConcreteBitVecDomain
    if a.is_bool():
        return ConcreteBoolDomain
    if a.is_bytes():
        return ConcreteBytesDomain
    if a.is_float():
        return ConcreteFloatsDomain
    raise NotImplementedError(f"Unknown domain for value: {a}")


def get_any_domain_checked(a: Value, b: Value):
    assert isinstance(a, ConcreteVal), a
    assert isinstance(b, ConcreteVal), b
    assert a.type() == b.type(), f"{a.type()} != {b.type()}"
    assert a.bitwidth() == b.bitwidth(), f"{a}, {b}"

    if a.is_bv():
        return ConcreteBitVecDomain
    if a.is_bool():
        return ConcreteBoolDomain
    if a.is_bytes():
        return ConcreteBytesDomain
    if a.is_float():
        return ConcreteFloatsDomain
    raise NotImplementedError(f"Unknown domain for value: {a}")


def get_bv_bytes_domain(a: Value):
    assert isinstance(a, (ConcreteBitVec, ConcreteBytes)), a
    if a.is_bv():
        return ConcreteBitVecDomain
    if a.is_bytes():
        return ConcreteBytesDomain
    raise NotImplementedError(f"Unknown domain for value: {a}")


def get_bv_bytes_domain_checked(a: Value, b: Value):
    assert isinstance(a, (ConcreteBitVec, ConcreteBytes)), a
    assert isinstance(b, (ConcreteBitVec, ConcreteBytes)), b
    assert a.type() == b.type(), f"{a.type()} != {b.type()}"
    assert a.bitwidth() == b.bitwidth(), f"{a}, {b}"
    if a.is_bv():
        return ConcreteBitVecDomain
    if a.is_bytes():
        return ConcreteBytesDomain
    raise NotImplementedError(f"Unknown domain for value: {a}")


def lower_bytes(x):
    if isinstance(x, ConcreteBytes) and x.bitwidth() <= 64:
        x.to_bv()
    return x


class ConcreteDomain(Domain):
    """
    Takes care of handling concrete computations.
    """

    @staticmethod
    def get_value(c: int, bw_or_ty: Union[Type, int]) -> ConcreteVal:
        if isinstance(bw_or_ty, int):
            bw = bw_or_ty
            if isinstance(c, bool):
                assert bw == 1, bw
                return ConcreteBool(c)
            if isinstance(c, int):
                return ConcreteBitVec(c, bw)
            if isinstance(c, (float, float64)):
                return ConcreteFloat(c, bw)
        elif isinstance(bw_or_ty, Type):
            if bw_or_ty.is_bool():
                return ConcreteBool(c)
            if bw_or_ty.is_bv():
                return ConcreteBitVec(c, bw_or_ty)
            if bw_or_ty.is_float():
                return ConcreteFloat(c, bw_or_ty)
        raise NotImplementedError(
            "Don't know how to create a ConcretValue for {c}: {type(c)}"
        )

    @staticmethod
    def get_true() -> ConcreteBool:
        return ConcreteBool(True)

    @staticmethod
    def get_false() -> ConcreteBool:
        return ConcreteBool(False)

    @staticmethod
    def conjunction(*args) -> ConcreteBool:
        assert all((isinstance(a, ConcreteBool) for a in args)), args
        assert all((a.is_bool() for a in args))
        return ConcreteBoolDomain.conjunction(*args)

    @staticmethod
    def disjunction(*args) -> ConcreteBool:
        assert all((isinstance(a, ConcreteBool) for a in args)), args
        assert all((a.is_bool() for a in args))
        return ConcreteBoolDomain.disjunction(*args)

    @staticmethod
    def And(a: Value, b: Value) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).And(a, b)

    @staticmethod
    def Or(a: ConcreteVal, b: ConcreteVal) -> ConcreteVal:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Or(a, b)

    @staticmethod
    def Xor(a: ConcreteVal, b: ConcreteVal) -> ConcreteVal:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Xor(a, b)

    @staticmethod
    def Not(a: ConcreteVal) -> ConcreteVal:
        assert isinstance(a, ConcreteVal), a
        if a.is_bool():
            return ConcreteBoolDomain.Not(a)
        raise NotImplementedError(f"Operation not implemented: Not({a})")

    @staticmethod
    def Extend(a: ConcreteVal, b: int, unsigned: bool) -> Value:
        assert isinstance(a, ConcreteVal), a
        assert isinstance(b, int), b
        assert not a.is_float(), "No extend for floats implemented"
        a = lower_bytes(a)
        return get_any_domain(a).Extend(a, b, unsigned)

    @staticmethod
    def Cast(a: Value, ty: Type, signed: bool = False) -> Optional[Value]:
        """Reinterpret cast"""

        assert isinstance(a, ConcreteVal), a
        bw = ty.bitwidth()
        if a.is_bool() and ty.is_bv():
            return ConcreteBitVec(1 if a.value() != 0 else 0, bw)
        if a.is_bytes():
            if ty.is_bv():
                return a.to_bv()
            if ty.is_float():
                return ConcreteFloat(to_fp(a, bw), bw)
        if a.is_bv():
            if ty.is_float():
                return ConcreteFloat(a.value(), bw)
            elif ty.is_bv():
                return ConcreteBitVec(a.value(), bw)
            elif ty.is_bool():
                return ConcreteBool(False if a.value() == 0 else True)
        elif a.is_float():
            if ty.is_float():
                return ConcreteFloat(a.value(), bw)
            elif ty.is_bv():
                return ConcreteBitVec(float_to_bv(a, bw), bw)
        return None  # unsupported conversion

    @staticmethod
    def BitCast(a: Value, ty: Type) -> Optional[ConcreteVal]:
        """static cast"""
        assert isinstance(a, ConcreteVal), a
        bw = ty.bitwidth()
        if a.is_bool() and ty.is_bv():
            return ConcreteBitVec(1 if a.value() else 0, bw)
        if a.is_bytes():
            if ty.is_float():
                return ConcreteFloat(to_fp(a.to_bv(), bw), bw)
            if ty.is_bv():
                return a.to_bv()
        if a.is_bv():
            if ty.is_float():
                return ConcreteFloat(to_fp(a, bw), bw)
            elif ty.is_bv():
                return ConcreteBitVec(a.value(), bw)
            elif ty.is_bool():
                return ConcreteBool(False if a.value() == 0 else True)
            elif ty.is_bytes():
                return ConcreteBytes(
                    [
                        ConcreteBitVec(val, 8)
                        for val in int_to_bytes(a.value(), a.bytewidth())
                    ]
                )
        elif a.is_float():
            if ty.is_float():
                return ConcreteFloat(a.value(), bw)
            elif ty.is_bytes():
                return ConcreteBytes(
                    [
                        ConcreteBitVec(val, 8)
                        for val in concrete_float_val_to_bytes(a.value())
                    ]
                )
            elif ty.is_bv():
                return ConcreteBitVec(float_to_bv(a, bw), bw)
            return None  # unsupported conversion

    def IntOp(op, val: Value, val2: Value):
        assert val is not None
        assert val2 is not None
        assert val.type() == val2.type()
        assert isinstance(val, ConcreteVal)
        assert isinstance(val2, ConcreteVal)

        bw = val.bitwidth()
        v1, v2 = to_signed(val.value(), bw), to_signed(val2.value(), bw)
        if op == IntOp.ADD_DONT_OVERFLOW:
            # we use the fact that Python int is arbitrary precision!
            return ConcreteBool(v1 + v2 <= ((1 << (bw - 1)) - 1))
        if op == IntOp.ADD_DONT_UNDERFLOW:
            return ConcreteBool(v1 + v2 >= -(1 << (bw - 1)))
        if op == IntOp.SUB_DONT_OVERFLOW:
            # we use the fact that Python int is arbitrary precision!
            return ConcreteBool(v1 - v2 <= ((1 << (bw - 1)) - 1))
        if op == IntOp.SUB_DONT_UNDERFLOW:
            return ConcreteBool(v1 - v2 >= -(1 << (bw - 1)))
        if op == IntOp.MUL_DONT_OVERFLOW:
            # we use the fact that Python int is arbitrary precision!
            return ConcreteBool(v1 * v2 <= ((1 << (bw - 1)) - 1))
        if op == IntOp.MUL_DONT_UNDERFLOW:
            return ConcreteBool(v1 * v2 >= -(1 << (bw - 1)))
        if op == IntOp.DIV_DONT_OVERFLOW:
            # we use the fact that Python int is arbitrary precision!
            return ConcreteBool(int(v1 / v2) <= ((1 << (bw - 1)) - 1))

        return None

    @staticmethod
    def Shl(a: Value, b: Value) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_bv_bytes_domain_checked(a, b).Shl(a, b)

    @staticmethod
    def AShr(a: Value, b: Value) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_bv_bytes_domain_checked(a, b).AShr(a, b)

    @staticmethod
    def LShr(a: Value, b: Value) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_bv_bytes_domain_checked(a, b).LShr(a, b)

    @staticmethod
    def Extract(a: Value, start: int, end: int) -> Value:
        assert isinstance(a, ConcreteBitVec), a
        assert isinstance(start, int), start
        assert isinstance(end, int), end
        a = lower_bytes(a)
        return get_bv_bytes_domain(a).Extract(a, start, end)

    @staticmethod
    def Concat(*args) -> Value:
        assert len(args) > 0, args
        return get_bv_bytes_domain(args[0]).Concat(*args)

    @staticmethod
    def Rem(a: Value, b: Value, unsigned: bool = False) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_bv_bytes_domain_checked(a, b).Rem(a, b, unsigned)

    @staticmethod
    def Neg(a: Value) -> Value:
        """Return the negated number"""
        return get_any_domain(a).Neg(a)

    @staticmethod
    def Abs(a: Value) -> Value:
        return get_any_domain(a).Abs(a)

    @staticmethod
    def FpOp(op, val: Value, val2: Value):
        return ConcreteFloatsDomain.FpOp(op, val, val2)

    ##
    # Relational operators
    @staticmethod
    def Le(a: ConcreteVal, b: ConcreteVal, unsigned: bool = False) -> ConcreteBool:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Le(a, b, unsigned)

    @staticmethod
    def Lt(a: ConcreteVal, b: ConcreteVal, unsigned: bool = False) -> ConcreteBool:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Lt(a, b, unsigned)

    @staticmethod
    def Ge(a: ConcreteVal, b: ConcreteVal, unsigned: bool = False) -> ConcreteBool:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Ge(a, b, unsigned)

    @staticmethod
    def Gt(a: ConcreteVal, b: ConcreteVal, unsigned: bool = False) -> ConcreteBool:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Gt(a, b, unsigned)

    @staticmethod
    def Eq(a: Value, b: Value, unsigned: bool = False) -> ConcreteBool:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Eq(a, b, unsigned)

    @staticmethod
    def Ne(a: Value, b: Value, unsigned: bool = False) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Ne(a, b, unsigned)

    ##
    # Arithmetic operations
    @staticmethod
    def Add(a: Value, b: Value) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Add(a, b)

    @staticmethod
    def Sub(a: ConcreteVal, b: ConcreteVal) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Sub(a, b)

    @staticmethod
    def Mul(a: Value, b: Value) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Mul(a, b)

    @staticmethod
    def Div(a: ConcreteBitVec, b: ConcreteBitVec, unsigned: bool = False) -> Value:
        a, b = lower_bytes(a), lower_bytes(b)
        return get_any_domain_checked(a, b).Div(a, b, unsigned)


ConstantTrue = ConcreteBool(True)
ConstantFalse = ConcreteBool(False)
concrete_value = ConcreteDomain.get_value

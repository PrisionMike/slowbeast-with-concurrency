from struct import unpack, pack
from typing import List, Optional, Sized, Union

from llvmlite.binding.module import ModuleRef
from llvmlite.binding.value import TypeRef, ValueRef

from slowbeast.domains.concrete import ConstantTrue, ConstantFalse, ConcreteDomain
from slowbeast.domains.concrete_bitvec import ConcreteBitVec
from slowbeast.domains.concrete_bytes import ConcreteBytes
from slowbeast.domains.concrete_value import ConcreteVal, ConcreteBool
from slowbeast.domains.pointer import Pointer, get_null_pointer
from slowbeast.ir.types import type_mgr, get_pointer_bitwidth
from slowbeast.util.debugging import warn

concrete_value = ConcreteDomain.get_value


def _getInt(s: str) -> Optional[int]:
    try:
        if s.startswith("0x"):
            return int(s, 16)
        else:
            if "e" in s:  # scientific notation
                if float(s) > 0 or float(s) < 0:
                    warn(f"Concretized float number: {s}")
                    # return None
                return int(float(s))
            else:
                return int(s)
    except ValueError:
        return None


def trunc_to_float(x):
    return unpack("f", pack("f", x))[0]


def to_float_ty(val: ConcreteVal) -> ConcreteVal:
    if isinstance(val, ConcreteVal):
        return concrete_value(float(val.value()), val.bitwidth())
    return val


def _get_float(s):
    try:
        if s.startswith("0x"):
            # llvm writes the constants as double
            # FIXME: get the byte order from module
            return trunc_to_float(unpack(">d", int(s, 16).to_bytes(8, "big"))[0])
        else:
            return float(s)
    except ValueError:
        return None


def _get_double(s, bw):
    try:
        if s.startswith("0x"):
            if s.startswith("0xK"):
                s = f"0x{s[3:]}"
                bts = 10
                return ConcreteBytes(
                    [concrete_value(b, 8) for b in int(s, 16).to_bytes(bts, "big")]
                )
            elif s.startswith("0xL"):
                s = f"0x{s[3:]}"
                bts = 16
                return ConcreteBytes(
                    [concrete_value(b, 8) for b in int(s, 16).to_bytes(bts, "big")]
                )
            else:
                bts = 8
                # llvm writes the constants as double (even when it is 32 bit)
                return concrete_value(
                    unpack(">d", int(s, 16).to_bytes(bts, "big"))[0], bw
                )
        else:
            return concrete_value(float(s), bw)
    except ValueError as e:
        print(float(int(s)))
        warn(f"Failed parsing a float constant '{s}': {e}")
        return None


def _bitwidth(ty: Sized) -> Optional[int]:
    if len(ty) < 2:
        return None
    if ty[0] == "i":
        return _getInt(ty[1:])
    elif ty.startswith("double"):
        # FIXME: get this from program - SSD - Should we?
        return 64
    elif ty.startswith("float"):
        return 32
    elif ty.startswith("x86_fp80"):
        return 80
    else:
        return None


def is_pointer_ty(ty: str) -> bool:
    if isinstance(ty, str):
        return ty[-1] == "*"

    assert ty.is_pointer == is_pointer_ty(str(ty))
    return ty.is_pointer


def is_array_ty(ty: str) -> bool:
    if isinstance(ty, str):
        if len(ty) < 2:
            return False
        return ty[0] == "[" and ty[-1] == "]"
    assert ty.is_array == is_array_ty(str(ty))
    return ty.is_array


def parse_array_ty(ty: TypeRef) -> None:
    parts = str(ty)[1:-1].split("x")
    return int(parts[0]), parts[1].strip()


def get_array_ty_size(m, ty: str) -> int:
    assert is_array_ty(ty)
    sty = str(ty)
    parts = sty.split()
    assert parts[1] == "x", "Invalid array type"
    assert parts[0].startswith("[")
    assert parts[-1].endswith("]")
    return int(parts[0][1:]) * type_size_in_bits(m, " ".join(parts[2:])[:-1])

def ty_is_sized(ty):
    # FIXME: do this properly
    return 'opaque' not in str(ty)


def type_size_in_bits(m: ModuleRef, ty: str) -> Optional[int]:
    if not ty_is_sized(ty):
        return None

    if not isinstance(ty, str) and hasattr(m, "get_type_size"):
        return m.get_type_size(ty)

    # FIXME: get rid of parsing str
    # FIXME: get rid of the magic constants and use the layout from the program
    POINTER_SIZE = get_pointer_bitwidth()
    if not isinstance(ty, str):
        if ty.is_pointer:
            return POINTER_SIZE
        if ty.is_struct:
            return None  # unsupported

    sty = str(ty)
    if is_array_ty(ty):
        return get_array_ty_size(m, ty)
    elif is_pointer_ty(ty):
        return POINTER_SIZE
    elif sty == "double":
        return 64
    elif sty == "float":
        return 32
    else:
        assert "*" not in sty, f"Unsupported type: {sty}"
        return _bitwidth(sty)
    return None


def type_size(m: ModuleRef, ty: str) -> Optional[int]:
    ts = type_size_in_bits(m, ty)
    if ts is not None:
        if ts == 0:
            return 0
        return int(max(ts / 8, 1))
    return None


def get_sb_type(m: ModuleRef, ty: str):
    if is_pointer_ty(ty):
        return type_mgr().pointer_ty()

    if is_array_ty(ty):
        # n, cty = parse_array_ty(ty)
        return type_mgr().bytes_ty(type_size(m, ty))

    sty = str(ty)
    if sty in ("void", "metadata"):
        return None

    ts = type_size_in_bits(m, ty)
    if ts is None:
        return None

    if sty in ("float", "double", "x86_fp80"):
        return type_mgr().float_ty(ts)
    elif sty.startswith("i"):
        return type_mgr().bv_ty(ts)

    if ty.is_struct:
        return type_mgr().bytes_ty(type_size_in_bits(m, ty))

    assert False, f"Unsupported type: {ty}"
    return None


def get_float_constant(sval, bw, isdouble: bool = True):
    if isdouble:
        return _get_double(sval, bw)
    return concrete_value(_get_float(sval), bw)


def get_pointer_constant(val) -> Optional[Pointer]:
    assert is_pointer_ty(val.type)
    parts = str(val).split()
    if parts[-1] == "null":
        return get_null_pointer()
    return None


def get_constant(val: ValueRef) -> Optional[ConcreteVal]:
    # My, this is so ugly... but llvmlite does
    # not provide any other way...
    if is_pointer_ty(val.type):
        return get_pointer_constant(val)

    sval = str(val)
    parts = sval.split()
    if is_array_ty(val.type):
        if parts[1] == "x" and parts[2].endswith("i8]") and parts[3].startswith('c"'):
            # this is a string
            s = sval[sval.find("x i8] c") + 7 :]
            ss = s[1:-1]
            assert s[0] == s[-1] == '"'
            bts = llvm_string_to_bytes(ss)
            return ConcreteBytes(bts)

    if len(parts) != 2:
        return None
    bw = _bitwidth(parts[0])
    if not bw:
        return None
    isdouble = parts[0] in ("double", "x86_fp80")
    isfloating = parts[0] == "float" or isdouble

    if isfloating:
        return get_float_constant(parts[1], bw, isdouble)

    c = _getInt(parts[1])
    if c is None:
        if bw == 1:
            if parts[1] == "true":
                c = True
            elif parts[1] == "false":
                c = False
        else:
            return None

    return concrete_value(c, bw)


def llvm_string_to_bytes(ss):
    bts = []
    end = len(ss)
    i = 0
    while i < end:
        c = ss[i]
        if c == "\\":
            # escape character, the value are the next two digits
            bts.append(ConcreteBitVec(int(ss[i + 1 : i + 2], 16), 8))
            i += 3
        else:
            bts.append(ConcreteBitVec(int(ord(c)), 8))
            i += 1
    return bts


def bv_to_bool_else_id(bv: ConcreteBool) -> ConcreteBool:
    if bv.is_concrete():
        if bv.value() == 0:
            return ConstantFalse
        else:
            return ConstantTrue
    return bv


def get_llvm_operands(inst: ValueRef) -> List[ValueRef]:
    return [x for x in inst.operands]

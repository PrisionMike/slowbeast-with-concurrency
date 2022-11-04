from typing import Union, List, Tuple, Optional

from slowbeast.core.errors import MemError
from slowbeast.core.memoryobject import MemoryObject as CoreMO
from slowbeast.domains.concrete_bitvec import ConcreteBitVec
from slowbeast.domains.concrete_bytes import ConcreteBytes
from slowbeast.domains.concrete_value import ConcreteVal
from slowbeast.domains.expr import Expr
from slowbeast.domains.value import Value
from slowbeast.ir.types import get_offset_type, type_mgr
from slowbeast.solvers.symcrete import global_expr_mgr
from slowbeast.util.debugging import dbgv


def get_byte(EM, x, bw, i: int):
    off = 8 * i
    b = EM.Extract(x, off, off + 7)
    assert b.bitwidth() == 8
    return b


def to_byte(x):
    assert x.bitwidth() == 8
    if isinstance(x, ConcreteBytes):
        return x
    if isinstance(x, ConcreteBitVec):
        return ConcreteBytes(x.value(), 1)
    return x


def write_bytes(offval, values, size, x: Union[Expr, Value]) -> Optional[MemError]:
    EM = global_expr_mgr()
    bw = x.bytewidth()
    if not x.is_bv():
        # rename to Cast and Cast to ReinterpretCast
        newx = EM.BitCast(x, type_mgr().bv_ty(8 * bw))
        if newx is None:
            return MemError(
                MemError.UNSUPPORTED, f"Cast of {x} to i{bw} is unsupported"
            )
        x = newx
    n = 0
    for i in range(offval, offval + bw):
        b = get_byte(EM, x, bw, n)
        values[i] = b
        n += 1
    return None


def read_bytes(values, offval, size, bts, zeroed):
    assert bts > 0, bts
    assert size > 0, size
    assert offval >= 0, offval
    expr_mgr = global_expr_mgr()
    if zeroed:
        c = offval + bts - 1
        # just make Extract return BytesType and it should work well then
        val = expr_mgr.Concat(
            *(
                values[c - i] if values[c - i] else ConcreteBytes(0, 1)
                for i in range(0, bts)
            )
        )
    else:
        if offval + bts > len(values):
            return None, MemError(
                MemError.UNINIT_READ,
                f"Read of {bts} bytes on offset {offval} "
                f"from object with {len(values)} initialized "
                "values.",
            )
        if not all(values[i] for i in range(offval, offval + bts)):
            return None, MemError(MemError.UNINIT_READ, "Read of uninitialized byte")
        c = offval + bts - 1
        # just make Extract return BytesType and it should work well then
        val = expr_mgr.Concat(*(to_byte(values[c - i]) for i in range(0, bts)))
    return val, None


def mo_to_bytes(values, size) -> Tuple[Optional[List[None]], Optional[MemError]]:
    dbgv("Promoting MO to bytes", color="gray")
    newvalues = [None] * size
    for o, val in values.items():
        tmp = write_bytes(o, newvalues, size, val)
        if tmp is not None:
            return None, tmp
    # if __debug__:
    #    rval, err = read_bytes(newvalues, o, size, val.bytewidth(), False)
    #    assert err is None
    #    crval = global_expr_mgr().Cast(rval, val.type())
    #    assert val == crval, f"{cval} ({rval}) != {val}"
    return newvalues, None


MAX_BYTES_SIZE = 64


class MemoryObject(CoreMO):
    __slots__ = ()

    # FIXME: refactor
    def read(
        self, bts: int, off: Optional[ConcreteVal] = None
    ) -> Union[Tuple[Expr, None], Tuple[ConcreteBitVec, None]]:
        """
        Read 'bts' bytes from offset 'off'. Return (value, None)
        on success otherwise return (None, error)
        """
        assert isinstance(bts, int), "Read non-constant number of bytes"
        if off is None:
            off = ConcreteBitVec(0, get_offset_type())

        if not off.is_concrete():
            return None, MemError(
                MemError.UNSUPPORTED, "Read from non-constant offset not supported"
            )

        size = self.size()
        if not size.is_concrete():
            return None, MemError(
                MemError.UNSUPPORTED,
                "Read from symbolic-sized objects not implemented yet",
            )

        assert size.is_bv(), size
        offval = off.value()
        size = size.value()

        if size < bts:
            return None, MemError(
                MemError.OOB_ACCESS, f"Read {bts}B from object of size {size}"
            )

        values = self._values
        if isinstance(values, list):
            return read_bytes(values, offval, size, bts, self._zeroed)

        val = values.get(offval)
        if val is None:
            if size <= MAX_BYTES_SIZE:
                values, err = mo_to_bytes(values, size)
                if err:
                    return None, err
                self._values = values
                assert isinstance(self._values, list)
                return read_bytes(values, offval, size, bts, self._zeroed)

            if self._zeroed:
                return ConcreteBitVec(0, bts * 8), None
            return None, MemError(
                MemError.UNINIT_READ,
                "uninitialized or unaligned read (the latter is unsupported)\n"
                f"Reading bytes {offval}-{offval + bts - 1} from obj {self._id} with contents:\n"
                f"{values}",
            )

        valbw = val.bytewidth()
        if valbw != bts:
            if size <= MAX_BYTES_SIZE:
                values, err = mo_to_bytes(values, size)
                if err:
                    return None, err
                self._values = values
                return read_bytes(values, offval, size, bts, self._zeroed)

            return None, MemError(
                MemError.UNSUPPORTED,
                "Reading bytes from object defined by parts is unsupported atm: "
                f"reading {bts} bytes from off {offval} where is value with "
                f"{val.bytewidth()} bytes",
            )

        # FIXME: make me return BytesType objects (a sequence of bytes)
        return val, None

    def write(self, x: Value, off: Optional[ConcreteVal] = None) -> Optional[MemError]:
        """
        Write 'x' to 'off' offset in this object.
        Return None if everything is fine, otherwise return the error
        """
        assert isinstance(x, Value)
        assert self._ro is False, "Writing read-only object (COW bug)"

        if off is None:
            off = ConcreteBitVec(0, get_offset_type())

        if not off.is_concrete():
            return MemError(
                MemError.UNSUPPORTED, "Write to non-constant offset not supported"
            )

        if not self.size().is_concrete():
            return MemError(
                MemError.UNSUPPORTED,
                "Write to symbolic-sized objects not implemented yet",
            )

        size = self.size().value()
        offval = off.value()

        if x.bytewidth() > size + offval:
            return MemError(
                MemError.OOB_ACCESS,
                "Written value too big for the object. "
                "Writing {0}B to offset {1} of {2}B object".format(
                    x.bytewidth(), offval, size
                ),
            )

        values = self._values
        if isinstance(values, list):
            return write_bytes(offval, values, size, x)
        else:
            # does the write overlap? should we promote the object
            # to bytes-object?
            # FIXME: not efficient...
            bw = x.bytewidth()
            for o, val in values.items():
                if offval < o + val.bytewidth() and offval + bw > o:
                    if o == offval and val.bytewidth() == bw:
                        break  # the overlap is perfect, we just overwrite
                        # the value
                    if size <= MAX_BYTES_SIZE:  # For now...
                        # promote to bytes
                        tmp, err = mo_to_bytes(values, size)
                        if err:
                            return err
                        self._values = tmp
                        return write_bytes(offval, tmp, size, x)
                    return MemError(
                        MemError.UNSUPPORTED, "Overlapping writes to memory"
                    )

            values[offval] = x
            return None
        return MemError(MemError.UNSUPPORTED, "Unsupported memory operation")

    def __repr__(self) -> str:
        s = self._repr_header()
        vals = self._values
        for k, v in enumerate(vals) if isinstance(vals, list) else vals.items():
            s += f"\n  {k} -> {v}"
        return s

from slowbeast.ir.types import OffsetType, IntType
from slowbeast.domains.concrete import ConcreteVal
from slowbeast.core.errors import MemError
from slowbeast.util.debugging import dbg
from slowbeast.core.memory import Memory as CoreMemory
from slowbeast.core.memoryobject import MemoryObject as CoreMO
from slowbeast.solvers.solver import getGlobalExprManager


class MemoryObject(CoreMO):

    def read(self, bts, off=ConcreteVal(0, OffsetType)):
        """
        Read 'bts' bytes from offset 'off'. Return (value, None)
        on success otherwise return (None, error)
        """
        assert isinstance(bts, int), "Read non-constant number of bytes"

        if not off.is_concrete():
            raise NotImplementedError("Read from non-constant offset not supported")

        if not self.getSize().is_concrete():
            raise NotImplementedError(
                "Read from symbolic-sized objects not implemented yet"
            )

        offval = off.value()

        if self.getSize().value() < bts:
            return None, MemError(
                MemError.OOB_ACCESS,
                "Read {0}B from object of size {1}B".format(bts, self.getSize()),
            )

        values = self.values
        val = values.get(offval)
        if val is None:
            # FIXME: a hack that works for some type of accesses
            # FIXME: until we have a proper byte-level memory objects
            o = offval - 4
            while o >= 0:
                predval = values.get(o)
                if predval is not None:
                    if predval.bytewidth() + o >= offval + bts - 1:
                        # the value on immediately lower offset perfectly overlaps with our read,
                        # extract the value from it
                        EM = getGlobalExprManager()
                        startb = offval - o
                        cast = EM.Cast(predval, IntType(predval.bitwidth()))
                        if cast:
                            extr = EM.Extract(cast,
                                              ConcreteVal(8*startb, OffsetType),
                                              ConcreteVal(8*(offval + bts)-1, OffsetType))
                            assert extr.bytewidth() == bts, extr
                            return extr, None
                        else:
                            dbg(f"Unsupported conversion from {predval.type()} to i{predval.bitwidth()}")
                            break
                    break
                o = o - 4

            return None, MemError(
                MemError.UNINIT_READ,
                f"Read from uninitialized memory (or unaligned read (not supp.  yet)).\n"
                f"Reading bytes {offval}-{offval+bts-1} from obj {self._id} with contents:\n"
                f"{self.values}",
            )

        valbw = val.bytewidth()
        if valbw != bts:
            # HACK!
            if offval == 0: # for != 0 we do not know if it has been overwritten
                if valbw > bts:
                    # truncate the value
                    EM = getGlobalExprManager()
                    extr = EM.Extract(EM.Cast(val, IntType(val.bitwidth())),
                                      ConcreteVal(0, OffsetType),
                                      ConcreteVal(8 * (offval + bts) - 1, OffsetType))
                    assert extr.bytewidth() == bts, extr
                    return extr, None
                else:
                    # join two consequiteve values if possible
                    nxtval = values.get(offval + valbw)
                    if nxtval and valbw + nxtval.bytewidth() >= bts:
                        EM = getGlobalExprManager()
                        extr = EM.Extract(EM.Cast(nxtval, IntType(val.bitwidth())),
                                          ConcreteVal(0, OffsetType),
                                          ConcreteVal(8 * (bts - valbw) - 1, OffsetType))
                        assert valbw + extr.bytewidth() == bts, extr
                        expr = EM.Concat(extr, val) # the values are store in little endian
                        assert expr.bytewidth() == bts, expr
                        return expr, None

            return None, MemError(
                MemError.UNSUPPORTED,
                f"Reading bytes from object defined by parts is unsupported atm: "
                f"reading {bts} bytes from off {offval} where is value with "
                f"{val.bytewidth()} bytes"
            )

        # FIXME: make me return Bytes objects (a sequence of bytes)
        return val, None


class Memory(CoreMemory):
    def createMO(self, size, nm=None, objid=None):
        """
        Create a new memory object -- may be overridden
        by child classes to create a different type of
        memory objects.
        """
        return MemoryObject(size, nm, objid)

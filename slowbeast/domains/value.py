#!/usr/bin/python

from typing import Union, Any

from z3.z3 import BitVecRef, BoolRef, FPRef

from slowbeast.ir.types import Type


class Value:
    __slots__ = "_type", "_value"

    def __init__(self, val: Any, ty: Type) -> None:
        assert isinstance(ty, Type)
        self._type = ty
        self._value = val

    def __eq__(self, other: object):
        return (
            isinstance(other, Value)
            and type(self) == type(other)
            and self._value == other._value
        )

    def unwrap(self) -> Union[BitVecRef, FPRef, BoolRef]:
        return self._value

    def value(self):
        return self._value

    def type(self) -> Type:
        return self._type

    def bytewidth(self) -> int:
        return self._type.bytewidth()

    def bitwidth(self) -> int:
        return self._type.bitwidth()

    def is_pointer(self) -> bool:
        return self._type.is_pointer()

    def is_bool(self) -> bool:
        return self._type.is_bool()

    def is_bv(self) -> bool:
        return self._type.is_bv()

    def is_float(self) -> bool:
        return self._type.is_float()

    def is_bytes(self) -> bool:
        return self._type.is_bytes()

    def is_symbolic(self):
        """
        Is integer constant or boolean constant?
        Overriden by the ConcreteVal class
        """
        raise NotImplementedError("Must be overriden")

    def is_concrete(self) -> bool:
        """
        Is this a concrete value? (syntactically)
        """
        return not self.is_symbolic()

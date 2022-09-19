from slowbeast.domains.concrete_value import ConcreteBool
from .domain import Domain


class ConcreteBoolDomain(Domain):

    @staticmethod
    def belongto(x) -> bool:
        return isinstance(x, ConcreteBool)

    @staticmethod
    def Value(c) -> ConcreteBool:
        assert isinstance(c, bool), c
        return ConcreteBool(c)

    @staticmethod
    def conjunction(*args) -> ConcreteBool:
        """ And() of multiple boolean arguments. """
        assert all(map(lambda a: ConcreteBoolDomain.belongto(a), args)), args
        assert all(map(lambda a: a.is_bool(), args))
        return ConcreteBool(all(map(lambda x: x.value() is True, args)))

    @staticmethod
    def disjunction(*args) -> ConcreteBool:
        """ Or() of multiple boolean arguments. """
        assert all(map(lambda a: ConcreteBoolDomain.belongto(a), args)), args
        assert all(map(lambda a: a.is_bool(), args))
        return ConcreteBool(any(map(lambda x: x.value() is True, args)))

    @staticmethod
    def Ite(c: Value, a: Value, b: Value) -> Value:
        assert ConcreteBoolDomain.belongto(c)
        assert c.is_bool(), c
        assert a.type() == b.type(), f"{a}, {b}"
        return a if c else b

    @staticmethod
    def And(a: Value, b: Value) -> ConcreteBool:
        assert ConcreteBoolDomain.belongto(a), a
        assert ConcreteBoolDomain.belongto(b), b
        assert a.is_bool(), a
        assert b.is_bool(), b
        return ConcreteBool(a.value() and b.value())

    @staticmethod
    def Or(a: Value, b: Value) -> ConcreteBool:
        assert ConcreteBoolDomain.belongto(a), a
        assert ConcreteBoolDomain.belongto(b), b
        assert a.is_bool(), a
        assert b.is_bool(), b
        return ConcreteBool(a.value() or b.value())

    @staticmethod
    def Xor(a: Value, b: Value) -> ConcreteBool:
        assert ConcreteBoolDomain.belongto(a), a
        assert ConcreteBoolDomain.belongto(b), b
        assert a.is_bool(), a
        assert b.is_bool(), b
        assert a.value() in (True, False),a
        assert b.value() in (True, False),b
        return ConcreteBool(a.value() ^ b.value())

    @staticmethod
    def Not(a: Value) -> ConcreteBool:
        assert ConcreteBoolDomain.belongto(a)
        assert a.is_bool(), a
        assert a.value() in (True, False),a
        return ConcreteBool(not a.value())

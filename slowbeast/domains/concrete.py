from .. ir.types import Type, BoolType
from .. ir.value import Value, Constant


class ConcreteDomain:
    """
    Takes care of handling concrete computations.
    """

    def belongto(*args):
        assert len(args) > 0
        for a in args:
            assert isinstance(a, Value)
            if not a.isConstant():
                return False
        return True

    def Constant(c, bw):
        if isinstance(c, bool):
            assertbw == 1
            return Constant(c, BoolType())
        return Constant(c, Type(bw))

    def And(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() and b.getValue(), BoolType())

    def Or(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() or b.getValue(), BoolType())

    def Not(a):
        assert ConcreteDomain.belongto(a)
        return Constant(not a.getValue(), BoolType())

    ##
    # Relational operators
    def Le(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() <= b.getValue(), BoolType())

    def Lt(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() < b.getValue(), BoolType())

    def Ge(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() >= b.getValue(), BoolType())

    def Gt(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() > b.getValue(), BoolType())

    def Eq(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() == b.getValue(), BoolType())

    def Ne(a, b):
        assert ConcreteDomain.belongto(a, b)
        return Constant(a.getValue() != b.getValue(), BoolType())

    ##
    # Arithmetic operations
    def Add(a, b):
        assert ConcreteDomain.belongto(a, b)
        result_ty = Type(max(a.getType().getBitWidth(),
                             b.getType().getBitWidth()))
        return Constant(a.getValue() + b.getValue(), result_ty)

    def Sub(a, b):
        assert ConcreteDomain.belongto(a, b)
        result_ty = Type(max(a.getType().getBitWidth(),
                             b.getType().getBitWidth()))
        return Constant(a.getValue() - b.getValue(), result_ty)

    def Mul(a, b):
        assert ConcreteDomain.belongto(a, b)
        result_ty = Type(2 * max(a.getType().getBitWidth(),
                                 b.getType().getBitWidth()))
        return Constant(a.getValue() * b.getValue(), result_ty)

    def Div(a, b):
        assert ConcreteDomain.belongto(a, b)
        result_ty = Type(max(a.getType().getBitWidth(),
                             b.getType().getBitWidth()))
        return Constant(a.getValue() / b.getValue(), result_ty)

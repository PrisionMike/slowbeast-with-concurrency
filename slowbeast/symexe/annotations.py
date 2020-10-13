from slowbeast.util.debugging import dbg, dbgv, dbg_sec, FIXME
from slowbeast.core.executor import split_ready_states
from slowbeast.domains.symbolic import NondetLoad

from . statedescription import StateDescription


class Annotation:
    ASSUME = 1
    ASSERT = 2
    INSTRS = 3

    __slots__ = ['type']

    def __init__(self, ty):
        assert ty >= Annotation.ASSUME and ty <= Annotation.INSTRS
        self.type = ty

    def isInstrs(self):
        return self.type == Annotation.INSTRS

    def isAssume(self):
        return self.type == Annotation.ASSUME

    def isAssert(self):
        return self.type == Annotation.ASSERT


class InstrsAnnotation(Annotation):
    """
    Annotation that is barely a sequence of instructions
    that should be executed
    """
    __slots__ = ['instrs']

    def __init__(self, instrs):
        super(InstrsAnnotation, self).__init__(Annotation.INSTRS)
        self.instrs = instrs

    def getInstructions(self):
        return self.instrs

    def __iter__(self):
        return self.instrs.__iter__()

    def __repr__(self):
        return "[{0}]".format(
            ", ".join(map(lambda i: i.asValue(), self.instrs)))

    def dump(self):
        print("InstrsAnnotation[")
        for i in self.instrs:
            print(f"  {i}")
        print("]")


class ExprAnnotation(Annotation):

    __slots__ = ['_sd', 'cannonical']

    def __init__(self, ty, expr, subs, EM):
        super(
            ExprAnnotation, self).__init__(ty)

        # state description
        self._sd = StateDescription(expr, subs)

        # cannonical form of the annotation (so that we can compare
        # annotations)
        self.cannonical = self._sd.cannonical(EM)

    def getExpr(self):
        return self._sd.getExpr()

    def getSubstitutions(self):
        return self._sd.getSubstitutions()

    def getCannonical(self):
        return self.cannonical

    def Not(self, EM):
        n = copy(self)  # to copy the type and methods
        n._sd = StateDescription(EM.Not(self._expr), self.getSubstitutions())
        n.cannonical = n._sd.cannonical(EM)
        return n

    def doSubs(self, state):
        return self._sd.doSubs(state)

    def __eq__(self, rhs):
        return self.cannonical == rhs.cannonical

    def __hash__(self):
        assert self.cannonical
        return self.cannonical.__hash__()

    def __repr__(self):
        assert self.cannonical
        return f"{self.cannonical}"
        # return "{0}[{1}]".format(self._expr, ",
        # ".join(f"{x.asValue()}/{val.unwrap()}" for (x, val) in
        # self.subs.items()))

    def dump(self):
        print(
            "ExprAnnotation[{0}]:".format(
                'assert' if self.type == Annotation.ASSERT else 'assume'))
        print(f"> expr: {self.getExpr()}")
        print(f"> cannonical: {self.getCannonical()}")
        print("> substitutions: {0}".format(", ".join(
            f"{x.asValue()}/{val.unwrap()}" for (val, x) in self.getSubstitutions().items())))


class AssertAnnotation(ExprAnnotation):
    def __init__(self, expr, subs, EM):
        super(
            AssertAnnotation,
            self).__init__(
            Annotation.ASSERT,
            expr,
            subs,
            EM)

    def toAssume(self, EM):
        return AssumeAnnotation(self.getExpr(), self.getSubstitutions(), EM)

    def __repr__(self):
        return f"assert {ExprAnnotation.__repr__(self)}"


class AssumeAnnotation(ExprAnnotation):
    def __init__(self, expr, subs, EM):
        super(
            AssumeAnnotation,
            self).__init__(
            Annotation.ASSUME,
            expr,
            subs,
            EM)

    def __repr__(self):
        return f"assume {ExprAnnotation.__repr__(self)}"


def _execute_instr(executor, states, instr):
    newstates = []
    for state in states:
        # FIXME: get rid of this -- make a version of
        # execute() that does not mess with pc
        oldpc = state.pc
        assert state.isReady()
        newstates += executor.execute(state, instr)

    ready, nonready = [], []
    for x in newstates:
        x.pc = oldpc
        (ready, nonready)[0 if x.isReady() else 1].append(x)
    return ready, nonready


def _execute_instr_annotation(executor, states, annot):
    nonready = []
    for instr in annot:
        states, u = _execute_instr(executor, states, instr)
        nonready += u
    return states, nonready


def _execute_expr_annotation(executor, states, annot):
    nonready = []

    subs = annot.getSubstitutions()
    for i in set(subs.values()):
        states, nr = _execute_instr(executor, states, i)
        nonready += nr

    isassume = annot.isAssume()
    expr = annot.getExpr()
    ready = states
    states = []
    for s in ready:
        expr = annot.doSubs(s)
        if isassume:
            dbg(f"assume {expr}")
            s = executor.assume(s, expr)
            if s:
                states.append(s)
        else:
            assert annot.isAssert()
            dbg(f"assert {expr}")
            tr, tu = split_ready_states(executor.execAssertExpr(s, expr))
            states += tr
            nonready += tu

    return states, nonready


def execute_annotation(executor, states, annot):
    """ Execute the given annotation on states """

    assert isinstance(annot, Annotation), annot
    assert all(map(lambda s: s.isReady(), states))

    dbg_sec(f"executing annotation:\n{annot}")

    if annot.isInstrs():
        states, nonready = _execute_instr_annotation(executor, states, annot)
    else:
        assert annot.isAssume() or annot.isAssert()
        states, nonready = _execute_expr_annotation(executor, states, annot)

    dbg_sec()
    return states, nonready


def execute_annotations(executor, s, annots):
    assert s.isReady(), "Cannot execute non-ready state"
    oldpc = s.pc

    dbg_sec(f"executing annotations on state {s.getID()}")

    ready, nonready = [s], []
    for annot in annots:
        ready, nr = execute_annotation(executor, ready, annot)
        nonready += nr

    assert all(map(lambda s: s.pc is oldpc, ready))

    dbg_sec()
    return ready, nonready


def unify_annotations(EM, annot1, annot2):
    """
    Take two annotations, unify their variables and substitutions.
    Return the new expressions and the substitutions
    """
    if annot1 is None:
        return None, annot2.getExpr(), annot2.getSubstitutions()
    if annot2 is None:
        return annot1.getExpr(), None, annot1.getSubstitutions()

    # perform less substitutions if possible
    subs1 = annot1.getSubstitutions()
    subs2 = annot2.getSubstitutions()
    expr1 = annot1.getExpr()
    expr2 = annot2.getExpr()
    if 0 < len(subs2) < len(subs1) or len(subs1) == 0:
        subs1, subs2 = subs2, subs1
        expr1, expr2 = expr2, expr1

    if len(subs1) == 0:
        assert len(subs2) == 0
        return EM.simplify(expr1), EM.simplify(expr2), {}

    subs = {}
    col = False
    for (val, instr) in subs1.items():
        instr2 = subs2.get(val)
        if instr2 and instr2 != instr:
            # collision
            freshval = EM.freshValue(
                val.name(), bw=val.getType().getBitWidth())
            expr2 = EM.substitute(expr2, (val, freshval))
            subs[freshval] = instr2

        # always add this one
        subs[val] = instr

    # add the rest of subs2
    for (val, instr) in subs2.items():
        if not subs.get(val):
            subs[val] = instr

    return EM.simplify(expr1), EM.simplify(expr2), subs


def _join_annotations(EM, Ctor, op, annots):
    assert len(annots) > 0
    if len(annots) == 1:
        return annots[0]

    simplify = EM.simplify
    subs = {}
    S = None
    for a in annots:
        expr1, expr2, subs = unify_annotations(EM, S, a)
        if expr1 and expr2:
            S = Ctor(simplify(op(expr1, expr2)), subs, EM)
        else:
            S = Ctor(expr1 or expr2, subs, EM)
    return S


def or_annotations(EM, toassert, *annots):
    assert isinstance(toassert, bool)
    assert all(map(lambda x: isinstance(x, ExprAnnotation), annots))

    Ctor = AssertAnnotation if toassert else AssumeAnnotation
    return _join_annotations(EM, Ctor, EM.Or, annots)


def and_annotations(EM, toassert, *annots):
    assert isinstance(toassert, bool)
    assert all(map(lambda x: isinstance(x, ExprAnnotation), annots))

    Ctor = AssertAnnotation if toassert else AssumeAnnotation
    return _join_annotations(EM, Ctor, EM.And, annots)


def state_to_annotation(state):
    EM = state.getExprManager()
    return AssumeAnnotation(state.getConstraintsObj().asFormula(EM),
                            {l: l.load for l in state.getNondetLoads()},
                            EM)


def states_to_annotation(states):
    a = None
    for s in states:
        EM = s.getExprManager()
        a = or_annotations(EM, False,
                           a or AssumeAnnotation(EM.getFalse(), {}, EM),
                           state_to_annotation(s))
    return a

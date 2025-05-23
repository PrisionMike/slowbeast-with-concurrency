from typing import Optional

from z3 import sat, unsat, unknown, Solver as Z3Solver, BoolVal, BitVecVal, FPVal
from z3.z3 import Solver

from slowbeast.domains.concrete import concrete_value


def to_z3_val(v):
    assert v.is_concrete(), v
    if v.is_bv():
        return BitVecVal(v.value(), v.type().bitwidth())
    if v.is_float():
        return FPVal(v.value(), v.type().bitwidth())

    raise NotImplementedError(f"Unimplemented converions: {v}")


def models(assumpt, *args):
    s = Z3Solver()
    for a in assumpt:
        assert a.is_bool(), a
        if a.is_concrete():
            s.add(a.value())
        else:
            s.add(a.unwrap())
    r = s.check()
    if r != sat:
        return None

    m = s.model()
    vals = []
    for a in args:
        # concrete values evaluate to concrete values
        if a.is_concrete():
            vals.append(to_z3_val(a))
            continue
        c = m.eval(a.unwrap(), True)
        if c is None:
            # m does not have a value for this variable
            # use 0
            c = BoolVal(False) if a.is_bool() else concrete_value(0, a.type())
        vals.append(c)

    return vals


def models_inc(solver, assumpt, *args):
    solver.push()
    for a in assumpt:
        assert a.is_bool()
        if a.is_concrete():
            solver.add(a.value())
        else:
            solver.add(a.unwrap())
    r = solver.check()
    if r != sat:
        solver.pop()
        return None

    m = solver.model()
    vals = []
    for a in args:
        # concrete values evaluate to concrete values
        if a.is_concrete():
            vals.append(a)
            continue
        c = m.eval(a.unwrap(), True)
        if c is None:
            # m does not have a value for this variable
            # use 0
            c = BoolVal(False) if a.is_bool() else concrete_value(0, a.type())
        vals.append(c)

    solver.pop()
    return vals


def _is_sat(solver: Solver, timeout: int, *args) -> Optional[bool]:
    if solver is None:
        solver = Z3Solver()

    if timeout:
        solver.set("timeout", timeout)
        r = solver.check(*args)
        solver.set("timeout", 4294967295)  # default value
    else:
        r = solver.check(*args)

    if r == sat:
        return True
    if r == unsat:
        return False
    if r == unknown:
        reason = solver.reason_unknown()
        if reason == "interrupted from keyboard":
            # If the user interrupted the computation,
            # re-raise the interrupt if it was consumed
            # in the solver so that the rest of the code
            # can react on it
            raise KeyboardInterrupt
    return None

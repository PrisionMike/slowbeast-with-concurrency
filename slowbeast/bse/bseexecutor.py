from sys import stdout
from slowbeast.symexe.pathexecutor import Executor as PathExecutor
from slowbeast.symexe.executionstate import LazySEState, Nondet
from slowbeast.symexe.annotations import ExprAnnotation, execute_annotation
from slowbeast.domains.pointer import Pointer
from slowbeast.domains.concrete import ConcreteInt
from slowbeast.ir.instruction import Load
from slowbeast.util.debugging import ldbgv
from .memorymodel import BSEMemoryModel, _nondet_value


def _subst_val(substitute, val, subs):
    assert isinstance(subs, tuple), subs
    assert len(subs) == 2, subs
    if subs[0].is_pointer():
        assert subs[1].is_pointer(), subs
        subs = (
            (subs[0].object(), subs[1].object()),
            (subs[0].offset(), subs[1].offset()),
        )
    else:
        assert not subs[1].is_pointer(), subs
        subs = (subs,)
    if val.is_pointer():
        return Pointer(substitute(val.object(), *subs), substitute(val.offset(), *subs))
    return substitute(val, *subs)


class BSEState(LazySEState):
    def __init__(self, executor=None, pc=None, m=None, solver=None, constraints=None):
        super().__init__(executor, pc, m, solver, constraints)
        # inputs are the subset of nondet values that we search for in pre-states
        # when joining states
        self._inputs = []

    def _copy_to(self, new):
        super()._copy_to(new)
        new._inputs = self._inputs.copy()

    def add_input(self, nd):
        self._inputs.append(nd)

    def inputs(self):
        return self._inputs

    def input(self, x):
        for nd in self._inputs:
            if nd.instruction == x:
                return nd
        return None

    def eval(self, v):
        value = self.try_eval(v)
        if value is None:
            value = _nondet_value(self.solver().fresh_value, v, v.type().bitwidth())
            ldbgv(
                "Created new input value {0} = {1}",
                (v.as_value(), value),
                color="dark_blue",
            )
            self.set(v, value)
            self.create_nondet(v, value)
            self.add_input(Nondet(v, value))
        assert value
        return value

    def memory_constraints(self):
        M = self.memory._reads
        em = self.expr_manager()
        Eq, And, Or, Not = em.Eq, em.And, em.Or, em.Not
        reads = list(M.items())
        constraints = []
        # FIXME: use enumerate()
        for idx1 in range(0, len(reads)):
            ptr1, val1 = reads[idx1]
            for idx2 in range(idx1 + 1, len(reads)):
                ptr2, val2 = reads[idx2]
                if val1 is val2 or val1.bitwidth() != val2.bitwidth():
                    continue
                # if the pointers are the same, the values must be the same
                if val1.is_pointer():
                    if val2.is_concrete() and val2.value() == 0:  # comparison to null
                        expr = And(Eq(val1.object(), val2), Eq(val1.offset(), val2))
                    else:
                        raise NotImplementedError(
                            "Comparison of symbolic addreses not implemented"
                        )
                elif val2.is_pointer():
                    if val1.is_concrete() and val1.value() == 0:  # comparison to null
                        expr = And(Eq(val2.object(), val1), Eq(val2.offset(), val1))
                    else:
                        raise NotImplementedError(
                            "Comparison of symbolic addreses not implemented"
                        )
                else:
                    expr = Eq(val1, val2)
                c = Or(
                    Not(
                        And(
                            Eq(ptr1.object(), ptr2.object()),
                            Eq(ptr1.offset(), ptr2.offset()),
                        )
                    ),
                    expr,
                )
                if c.is_concrete() and bool(c.value()):
                    continue
                constraints.append(c)
        return constraints

    def apply_postcondition(self, postcondition):
        if isinstance(postcondition, ExprAnnotation):
            good, _ = execute_annotation(self.executor(), [self], postcondition)
            return good
        raise NotImplementedError(f"Invalid post-condition: {postcondition}")

    def _replace_value(self, val, newval):
        em = self.expr_manager()
        # print('REPLACING', val, 'WITH', newval)

        # coerce the values
        if not val.is_bool() and newval.is_bool():
            assert val.bitwidth() == 1, val
            newval = em.Ite(newval, ConcreteInt(1, 1), ConcreteInt(0, 1))
        if not val.is_float() and newval.is_float():
            assert val.bitwidth() == newval.bitwidth()
            newval = em.Cast(newval, val.type())

        assert val.type() == newval.type(), f"{val} -- {newval}"
        # FIXME: use incremental solver
        substitute = em.substitute
        new_repl = []
        pc = self.path_condition()
        if val.is_pointer():
            assert val.object().is_concrete() or val.object().is_symbol(), f"Cannot replace {val} with {newval}"
            assert val.offset().is_concrete() or val.offset().is_symbol(), f"Cannot replace {val} with {newval}"
            # if the value is pointer, we must substitute it also in the state of the memory
            assert newval.is_pointer(), newval
            pc = substitute(
                pc, (val.object(), newval.object()), (val.offset(), newval.offset())
            )
        else:
            assert val.is_concrete() or val.is_symbol(), f"Cannot replace {val} with {newval}"
            pc = substitute(pc, (val, newval))
        self._replace_value_in_memory(new_repl, newval, substitute, val)
        self.set_constraints(pc)

        return new_repl

    def replace_value(self, val, newval):
        # recursively handle the implied equalities
        replace_value = self._replace_value
        new_repl = replace_value(val, newval)
        while new_repl:
            tmp = []
            for r in new_repl:
                tmp += replace_value(r[0], r[1])
            new_repl = tmp

    def _replace_value_in_memory(self, new_repl, newval, substitute, val):
        UP = self.memory._reads
        nUP = {}
        for cptr, cval in UP.items():
            nptr = _subst_val(substitute, cptr, (val, newval))
            nval = _subst_val(substitute, cval, (val, newval))

            curval = nUP.get(nptr)
            if curval:
                new_repl.append((curval, nval))
            nUP[nptr] = nval
        self.memory._reads = nUP

        UP = self.memory._input_reads
        nUP = {}
        # replace pointers in input reads, but not the values
        # we will need the values in substitutions
        for cptr, cval in UP.items():
            nptr = _subst_val(substitute, cptr, (val, newval))
            curval = nUP.get(nptr)
            if curval is not None:
                new_repl.append((curval[0], cval[0]))
            nUP[nptr] = cval
        self.memory._input_reads = nUP


    def _get_symbols(self):
        symbols = set(
            s for e in self.constraints() for s in e.symbols() if not e.is_concrete()
        )
        for ptr, val in self.memory._reads.items():
            symbols.update(ptr.symbols())
            symbols.update(val.symbols())
        for ptr, val in self.memory._input_reads.items():
            symbols.update(ptr.symbols())
            symbols.update(val[0].symbols())
        return symbols

    def join_prestate(self, prestate):
        """
        Update this state with information from prestate. That is, simulate
        that this state is executed after prestate.
        """
        assert isinstance(prestate, BSEState), type(prestate)
       #print("==================== Pre-state ========================")
       #prestate.dump()
       #print("==================== Join into ========================")
       #self.dump()
       #print("====================           ========================")
        try_eval = prestate.try_eval
        add_input = self.add_input

        ### modify the state according to the pre-state
        replace_value = self.replace_value
        for inp in self.inputs():
            preval = try_eval(inp.instruction)
            if preval:
                # print('REPL from reg', inp.value, preval)
                replace_value(inp.value, preval)

        new_ireads = {}
        for ptr, inpval in self.memory._input_reads.items():
            # try read the memory if it is written in the state
            val, _ = prestate.memory.read(ptr, inpval[1])
            if val:
                # print('REPL from memory', inp.value, val)
                replace_value(inpval[0], val)
            else:
                new_ireads[ptr] = inpval

        # filter the inputs that still need to be found and nondets that are still used
        symbols = set(self._get_symbols())
        self._inputs = [
            inp for inp in self.inputs() if not symbols.isdisjoint(inp.value.symbols())
        ]
        assert len(self._inputs) <= len(symbols)
        assert len(set(inp.instruction for inp in self._inputs)) == len(
            self._inputs
        ), f"Repeated value for an instruction: {self._inputs}"
        self._nondets = [
            inp for inp in self.nondets() if not symbols.isdisjoint(inp.value.symbols())
        ]
        assert len(self._nondets) <= len(symbols)

        ### copy the data from pre-state
        # add memory state from pre-state
        # FIXME: do not touch the internal attributes
        for k, v in prestate.memory._reads.items():
            if k not in self.memory._reads:
                self.memory._reads[k] = v
        self.memory._input_reads = prestate.memory._input_reads.copy()
        for k, v in new_ireads.items():
            if k not in self.memory._input_reads:
                self.memory._input_reads[k] = v
        # add new inputs from pre-state
        for inp in prestate.nondets():
            self.add_nondet(inp)
        for inp in prestate.inputs():
            add_input(inp)
        self.add_constraint(*prestate.constraints())

       #print("==================== Joined st ========================")
       #self.dump()
       #print("====================           ========================")
        if self.isfeasible():
            return [self]
        return []

    def __repr__(self):
        s = f"BSEState: {self.constraints()}"
        if self.memory._reads:
            s += "\n" + "\n".join(
                f"+L({p.as_value()})={x}" for p, x in self.memory._reads.items()
            )
        if self._inputs:
            s += "\n" + "\n".join(
                f"{nd.instruction.as_value()}={nd.value}" for nd in self._inputs
            )
        return s

    def dump(self, stream=stdout):
        super().dump(stream)
        write = stream.write
        write(" -- inputs --\n")
        for n in self._inputs:
            write(str(n))
            write("\n")


class Executor(PathExecutor):
    """
    Symbolic Executor instance adjusted to executing
    CFA paths possibly annotated with formulas.
    """

    def __init__(self, solver, opts, memorymodel=None):
        super().__init__(solver, opts, memorymodel or BSEMemoryModel(opts))

    def create_state(self, pc=None, m=None):
        """
        Overridden method for creating states.
        Since the path may not be initial, we must use states
        that are able to lazily create unknown values
        """
        if m is None:
            m = self.getMemoryModel().create_memory()
        s = BSEState(self, pc, m, self.solver)
        assert not s.constraints(), "the state is not clean"
        return s

    def execute_edge(self, states, edge, invariants=None):
        """
        states - pre-condition states (execute from these states)
        """
        assert all(map(lambda s: isinstance(s, LazySEState), states))

        source, target = edge.source(), edge.target()
        ready, nonready = states, []
        # annotations before taking the edge (proably an invariant)
        execannot = self.execute_annotations
        # annotations before source
        locannot = invariants.get(source) if invariants else None
        if locannot:
            ready, tu = execannot(ready, locannot)
            nonready += tu

        # execute the instructions from the edge
        if edge.is_assume():
            ready, tmpnonready = self._exec_assume_edge(ready, edge)
            nonready += tmpnonready
        elif edge.is_ret():
            # we handle passing return values manually in BSE, so just skip the return
            ldbgv("Skipping ret edge: {0}", (edge[0],))
        elif edge.is_call() and not edge.called_function().is_undefined():
            fn = edge.called_function().name()
            for s in ready:
                s.set_terminated(f"Called function {fn} on intraprocedural path")
                return [], nonready + ready
            raise NotImplementedError("Call edges not implemented")
        else:
            ready, tmpnonready = self.execute_seq(ready, edge)
            nonready += tmpnonready

        # annotations before target
        locannot = invariants.get(target) if invariants else None
        if locannot:
            assert all(
                map(lambda a: not a.isAssert(), locannot)
            ), f"An invariant is assertion: {locannot}"
            ready, tu = execannot(ready, locannot)
            nonready += tu
        # annotations after target

        return ready, nonready

    def execute_bse_path(self, states, path, invariants=None):
        badstates = []
        execute_edge = self.execute_edge
        for edge in path:
            states, tmpbad = execute_edge(states, edge, invariants)
            badstates.extend(tmpbad)
        return states, badstates

    #
    # def execute_annotated_edge(
    #     self,
    #     states,
    #     edge,
    #     pre=None,
    #     post=None,
    #     annot_before_loc=None,
    #     annot_after_loc=None,
    # ):
    #     """
    #     states - pre-condition states (execute from these states)
    #     """
    #     assert all(map(lambda s: isinstance(s, LazySEState), states))
    #
    #     source, target = edge.source(), edge.target()
    #     ready, nonready = states, []
    #     # annotations before taking the edge (proably an invariant)
    #     execannot = self.execute_annotations
    #     if pre:
    #         ready, tu = execannot(ready, pre)
    #         nonready += tu
    #     # annotations before source
    #     locannot = annot_before_loc(source) if annot_before_loc else None
    #     if locannot:
    #         ready, tu = execannot(ready, locannot)
    #         nonready += tu
    #     # annotations after source
    #     locannot = annot_after_loc(source) if annot_after_loc else None
    #     if locannot:
    #         ready, tu = execannot(ready, locannot)
    #         nonready += tu
    #
    #     # execute the instructions from the edge
    #     if edge.is_assume():
    #         ready, tmpnonready = self._exec_assume_edge(ready, edge)
    #         nonready += tmpnonready
    #     elif edge.is_call() and not edge.called_function().is_undefined():
    #         fn = edge.called_function().name()
    #         for s in ready:
    #             s.set_terminated(f"Called function {fn} on intraprocedural path")
    #             return [], nonready + ready
    #         raise NotImplementedError("Call edges not implemented")
    #     else:
    #         ready, tmpnonready = self.execute_seq(ready, edge)
    #         nonready += tmpnonready
    #
    #     # annotations before target
    #     locannot = annot_before_loc(target) if annot_before_loc else None
    #     if locannot:
    #         ready, tu = execannot(ready, locannot)
    #         nonready += tu
    #     # annotations after target
    #     locannot = annot_after_loc(target) if annot_after_loc else None
    #     if locannot:
    #         ready, tu = execannot(ready, locannot)
    #         nonready += tu
    #     if post:
    #         ready, tu = execannot(ready, post)
    #         nonready += tu
    #
    #     return ready, nonready

from slowbeast.core.executor import (
    PathExecutionResult,
    split_ready_states,
    split_nonready_states,
)
from slowbeast.util.debugging import dbgv, ldbgv
from .annotations import execute_annotations
from .executionstate import LazySEState
from .executor import Executor as SExecutor
from slowbeast.symexe.executionstate import LazySEState
from typing import Optional, Sized
from slowbeast.symexe.memorymodel import SymbolicMemoryModel


class Executor(SExecutor):
    """
    Symbolic Executor instance adjusted to executing
    CFA paths possibly annotated with formulas.
    """

    def __init__(
        self, program, solver, opts, memorymodel: Optional[SymbolicMemoryModel] = None
    ) -> None:
        super().__init__(program, solver, opts, memorymodel)

    def create_state(self, pc=None, m=None) -> LazySEState:
        """
        Overridden method for creating states.
        Since the path may not be initial, we must use states
        that are able to lazily create unknown values
        """
        if m is None:
            m = self.get_memory_model().create_memory()
        s = LazySEState(self, pc, m, self.solver)
        assert not s.constraints(), "the state is not clean"
        return s

    def exec_undef_fun(self, state, instr, fun):
        name = fun.name()
        if name == "abort":
            state.set_terminated("Aborted via an abort() call")
            return [state]

        retTy = fun.return_type()
        if retTy:
            val = state.solver().fresh_value(name, retTy)
            state.create_nondet(instr, val)
            state.set(instr, val)
        state.pc = state.pc.get_next_inst()
        return [state]

    def execute_annotations(self, states, annots):
        assert all(map(lambda s: isinstance(s, LazySEState), states))
        # if there are no annotations, return the original states
        if not annots:
            return states, []

        ready = []
        nonready = []

        for s in states:
            ts, tu = execute_annotations(self, s, annots)
            ready += ts
            nonready += tu
        assert all(map(lambda s: isinstance(s, LazySEState), ready)), "Wrong state type"
        return ready, nonready

    def _exec_assume_edge(self, states, edge):
        nonready = []
        isnot = edge.assume_false()
        for elem in edge:
            newstates = []
            for r in states:
                cond = r.eval(elem)
                # if cond is None:
                #    r.set_terminated(f"Invalid assume edge: {elem}")
                #    nonready.append(r)
                #    continue
                ldbgv(
                    "assume {0}{1}",
                    ("not " if isnot else "", cond),
                    verbose_lvl=3,
                    color="dark_green",
                )
                tmp = self.exec_assume_expr(
                    r, r.expr_manager().Not(cond) if isnot else cond
                )
                for t in tmp:
                    if t.is_ready():
                        newstates.append(t)
                    else:
                        nonready.append(t)
            states = newstates

        return states, nonready

    def _execute_annotated_edge(self, states, edge, path, pre=None):
        assert all(map(lambda s: isinstance(s, LazySEState), states))

        source = edge.source()
        ready, nonready = states, []
        # annotations before taking the edge (proably an invariant)
        execannot = self.execute_annotations
        if pre:
            ready, tu = execannot(ready, pre)
            nonready += tu
        # annotations before source
        locannot = path.annot_before_loc(source) if path else None
        if locannot:
            ready, tu = execannot(ready, locannot)
            nonready += tu
        # annotations after source
        locannot = path.annot_after_loc(source) if path else None
        if locannot:
            ready, tu = execannot(ready, locannot)
            nonready += tu

        # execute the instructions from the edge
        if edge.is_assume():
            ready, tmpnonready = self._exec_assume_edge(ready, edge)
            nonready += tmpnonready
        elif edge.is_call() and not edge.called_function().is_undefined():
            fn = edge.called_function().name()
            for s in ready:
                s.set_terminated(f"Called function {fn} on intraprocedural path")
                return [], nonready + ready
            raise NotImplementedError("Call edges not implemented")
        else:
            ready, tmpnonready = self.execute_seq(ready, edge)
            nonready += tmpnonready

        return ready, nonready

    def execute_annotated_path(
        self, state, path: Sized, invariants=None
    ) -> PathExecutionResult:
        """
        Execute the given path through CFG with annotations from the given
        state. NOTE: the passed states may be modified.

        All error and killed states met during the execution are counted
        as early terminated unless they are generated _after_ reaching
        the last location on the path. That is, the error states
        are those generated by annotations that follow the last location
        on the path.

        The method does not take into account whether the the last
        location is error or not. This must be handled in the top-level code.
        I.e., if the last location is error location, then the result.ready
        states are in fact error states (those that reach the error location
        and pass the annotations of this location).

        Invariants are assume annotations 'before' locations.
        """

        if isinstance(state, list):
            states = state
        else:
            states = [state]

        assert all(
            map(lambda s: isinstance(s, LazySEState), states)
        ), "Wrong state type"

        result = PathExecutionResult()
        earlytermstates = []
        edges = path.edges()
        execannots = self.execute_annotations

        # execute the precondition of the path
        pre = path.annot_before()
        if pre:
            states, tu = execannots(states, pre)
            earlytermstates += tu

        pathlen = len(path)
        assert all(
            map(lambda s: isinstance(s, LazySEState), states)
        ), "Wrong state type"
        for idx in range(pathlen):
            edge = edges[idx]
            dbgv(f"vv ----- Edge {edge} ----- vv", verbose_lvl=3)
            states, nonready = self._execute_annotated_edge(
                states,
                edge,
                path,
                invariants.get(edge.source()) if invariants else None,
            )
            assert all(
                map(lambda s: isinstance(s, LazySEState), states)
            ), "Wrong state type"
            assert all(map(lambda x: x.is_ready(), states))
            assert all(map(lambda x: not x.is_ready(), nonready))

            # now execute the branch following the edge on the path
            earlytermstates += nonready

            dbgv(f"^^ ----- Edge {edge} ----- ^^", verbose_lvl=3)
            if not states:
                dbgv("^^ (-8 Infeasible path 8-) ^^", verbose_lvl=3)
                break

        if states:
            # execute the annotations of the target (as _execute_annotated_edge
            # executes only the annotations of the source to avoid repetition)
            dbgv(">> Annotation of last loc + post", verbose_lvl=3)
            target = edge.target()
            locannot = path.annot_before_loc(target)
            if locannot and states:
                states, tu = execannots(states, locannot)
                # this annotation also counts as early terminating  as we still didn't
                # virtually get to the final location of the path
                earlytermstates += tu

            errors, other = [], []
            locannot = path.annot_after_loc(target)
            if locannot and states:
                states, tu = execannots(states, locannot)
                err, oth = split_nonready_states(tu)
                if err:
                    errors.extend(err)
                if oth:
                    other.extend(oth)
            # execute the postcondition of the path
            post = path.annot_after()
            if post and states:
                states, tu = execannots(states, post)
                err, oth = split_nonready_states(tu)
                if err:
                    errors.extend(err)
                if oth:
                    other.extend(oth)

            result.errors = errors or None
            result.other = other or None

        result.ready = states or None
        result.early = earlytermstates or None

        assert result.check(), "The states were partitioned incorrectly"
        return result


class CFGExecutor(SExecutor):
    """
    Symbolic Executor instance adjusted to executing
    paths possibly annotated with formulas.
    The paths are supposed to be AnnotatedCFGPaths (paths in CFG)
    """

    def __init__(
        self, program, solver, opts, memorymodel: Optional[SymbolicMemoryModel] = None
    ) -> None:
        super().__init__(program, solver, opts, memorymodel)

    def execute_annotations(self, states, annots):
        # if there are no annotations, return the original states
        if not annots:
            return states, []

        ready = []
        nonready = []

        for s in states:
            ts, tu = execute_annotations(self, s, annots)
            ready += ts
            nonready += tu
        return ready, nonready

    def execute_annotated_loc(self, states, loc, path=None):
        dbgv(f"vv ----- Loc {loc.bblock().get_id()} ----- vv", verbose_lvl=3)

        # execute annotations before bblock
        ready, nonready = self.execute_annotations(states, loc._annotations_before)
        locannot = path.get_loc_annots_before(loc) if path else None
        if locannot:
            ready, tu = self.execute_annotations(ready, locannot)
            nonready += tu

        # execute the block till branch
        states = self.execute_till_branch(ready, stopBefore=True)

        # get the ready states
        ready, tmpnonready = split_ready_states(states)
        nonready += tmpnonready

        # execute annotations after
        ready, tmpnonready = self.execute_annotations(ready, loc._annotations_after)
        nonready += tmpnonready

        locannot = path.get_loc_annots_after(loc) if path else None
        if locannot:
            ready, tu = self.execute_annotations(ready, locannot)
            nonready += tu

        dbgv(f"^^ ----- Loc {loc.bblock().get_id()} ----- ^^")
        return ready, nonready

    def execute_annotated_path(
        self, state, path, branch_on_last: bool = False
    ) -> PathExecutionResult:
        """
        Execute the given path through CFG with annotations from the given
        state. NOTE: the passed states may be modified.

        Return three lists of states.  The first list contains the states
        that reach the end of the path (i.e., the states after the execution of
        the last instruction on the path), the other list contains all other
        states, i.e., the error, killed or exited states reached during the
        execution of the CFG. Note that if the path is infeasible, this set
        contains no states.
        The last list contains states that terminate (e.g., are killed or are error
        states) during the execution of the path, but that does not reach the last
        step.

        If branch_on_last is set to True, instead of transfering control
        to the specified last point after executing all the previous points,
        normal fork is done (if there are multiple successors).
        That is, generate also states that avoid the last point
        at the path in one step.
        """

        if isinstance(state, list):
            states = state
        else:
            states = [state]

        result = PathExecutionResult()

        earlytermstates = []
        idx = 0

        locs = path.locations()
        # set the pc of the states to be the first instruction of the path
        newpc = locs[0].bblock().first()
        for s in states:
            s.pc = newpc

        # execute the precondition of the path
        pre = path.get_precondition()
        if pre:
            states, tu = self.execute_annotations(states, pre)
            earlytermstates += tu

        locsnum = len(locs)
        for idx in range(0, locsnum):
            loc = locs[idx]
            ready, nonready = self.execute_annotated_loc(states, loc, path)
            assert all(map(lambda x: x.is_ready(), ready))
            assert all(map(lambda x: isinstance(x.pc, Branch), ready)), [
                s.pc for s in ready
            ]

            # now execute the branch following the edge on the path
            if idx < locsnum - 1:
                earlytermstates += nonready

                # if this is the last edge and we should branch, do it
                if branch_on_last and idx == locsnum - 2:
                    newstates = self.execute_till_branch(ready)
                    assert all(map(lambda x: x.is_ready(), newstates))
                else:
                    curbb = loc.bblock()
                    succbb = locs[idx + 1].bblock()
                    followsucc = curbb.last().true_successor() == succbb
                    newstates = []
                    assert followsucc or curbb.last().false_successor() == succbb
                    for s in ready:
                        newstates += self.exec_branch_to(s, s.pc, followsucc)
            else:  # this is the last location on path,
                # so just normally execute the branch instruction in the block
                newstates = self.execute_till_branch(ready)
                # we executed only the branch inst, so the states still must be
                # ready
                assert all(map(lambda x: x.is_ready(), newstates))
                assert not result.errors, "Have unsafe states before the last location"
                result.errors, result.other = split_nonready_states(nonready)
            states = newstates
            if not states:
                break

        # execute the postcondition of the path
        post = path.get_postcondition()
        if post:
            states, tu = self.execute_annotations(states, post)
            result.errors, result.other = split_nonready_states(tu)

        result.ready = states or None
        result.early = earlytermstates or None

        assert result.check(), "The states were partitioned incorrectly"
        return result


# def substitute_constraints(constr, expr_mgr, prex, x):
#     newC = []
#     # FIXME: we need to do that at once!
#     for c in constr:
#         expr = expr_mgr.substitute(c, (x, prex))
#         if expr.is_concrete():
#             if expr.value() is False:
#                 return None  # infeasible constraints
#             elif expr.value() is not True:
#                 raise RuntimeError(f"Invalid constraint: {expr}")
#         else:
#             newC.append(expr)
#     return newC

# def join_states(self, fromstates, tostates):
#    dbg_sec("Joining states")
#    # join the states
#    finalstates = []
#    for r in fromstates:
#        expr_mgr = r.expr_manager()
#        for s in tostates:
#            tmpr = r.copy()
#            newconstr = s.constraints()

#            FIXME("Handle other nondets")  # FIXME
#            # map constraints from s to r
#            for x in (l for l in s.nondets() if l.is_nondet_load()):
#                prex = tmpr.get(x.load)
#                if not prex:
#                    res = self.execute(tmpr, x.load)
#                    assert len(res) == 1 and res[0] is tmpr
#                    prex = tmpr.get(x.load)
#                assert prex, "Do not have the value for x in pre-state"
#                if expr_mgr.equals(prex, x):
#                    continue  # no substitution needed
#                newconstr = substitute_constraints(newconstr, expr_mgr, prex, x)
#                if newconstr is None:
#                    tmpr = None
#                    break

#            if tmpr:
#                tmpr.add_constraint(*newconstr)
#                feas = tmpr.is_feasible()
#                assert feas is not None, "Solver failure"
#                if feas is True:
#                    finalstates.append(tmpr)

#    dbg_sec()
#    return finalstates

# def preimage(self, fromstate, tostates, path):
#    """
#    Get the states that make the execution
#    of path from 'fromstate' end up in 'tostates'
#    (ignoring pc of tostates).
#    NOTE: modifies 'fromstates'.
#    NOTE: This method does not set registers and memory
#    to mimic the execution of path -> tostates,
#    so it is sutiable only for computing the pre-condition
#    (the PC) of such path.
#    """

#    # execute the given path/block from 'fromstates'
#    dbg_sec("Computing preimage")
#    r = self.execute_annotated_path(fromstate, path)
#    finalstates = self.join_states(r.ready or [], tostates)

#    dbg_sec()
#    return finalstates

# def preimage(self, fromstates, tostates, blk):
#     """
#     Get the states that make the execution
#     of blk from 'fromstates' end up in 'tostates'.
#     NOTE: modifies 'fromstates'.
#     NOTE: This method does not set registers and memory
#     to mimic the execution of blk -> tostates,
#     so it is sutiable only for computing the pre-condition
#     (the PC) of such path.
#     """

#     # execute the given path/block from 'fromstates'
#     dbg_sec("Computing preimage")
#     ready = []
#     for s in fromstates:
#         s.pc = blk.first()
#         rdy = self.execute_till_branch(s)
#         for r in rdy:
#             if r.is_ready():
#                 ready.append(r)

#     finalstates = self.join_states(ready, tostates)

#     dbg_sec()
#     return finalstates

# def execute_annotated_step_with_prefixh(self, state, prefix):
#    """
#    Execute the given path through CFG with annotations from the given
#    state and then do one more step in CFG.

#    Returns three lists of states.
#    The first list contains safe states reachable after executing the 'path'
#    and doing one more step in CFG.
#    The second list contains unsafe states reachable after executing the 'path'
#    and doing one more step in CFG.
#    The last list contains states that terminate (e.g., are killed or are error
#    states) during the execution of the path, but that does not reach the last
#    step.
#    """

#    r = self.execute_annotated_path(state, prefix)
#    r.errors_to_early()
#    r.other_to_early()

#    dbg("Prefix executed, executing one more step")

#    # execute the last step -- all unsafe states are now really unsafe
#    cfg = prefix[0].get_cfg()
#    tmpready = []
#    nonready = []
#    if r.ready:
#        for s in r.ready:
#            # get the CFG node that is going to be executed
#            # (execute_annotated_path transferd the control to the right bblocks)
#            loc = cfg.get_node(s.pc.bblock())
#            ts, tu = self.execute_annotated_loc([s], loc, prefix)
#            tmpready += ts
#            nonready += tu

#    assert r.errors is None
#    assert r.other is None
#    r.errors, r.other = split_nonready_states(nonready)

#    dbg("Step executed, done.")
#    return r

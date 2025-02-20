from typing import Sized

from slowbeast.core.executionresult import PathExecutionResult
from slowbeast.symexe.state import LazySEState
from slowbeast.symexe.iexecutor import IExecutor
from slowbeast.util.debugging import ldbgv, dbgv


class PathIExecutor(IExecutor):
    """
    IExecutor with method to execute whole CFA paths
    """

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

    def _execute_edge(self, states, edge):
        assert all(map(lambda s: isinstance(s, LazySEState), states))
        ready, nonready = states, []

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

    def execute_path(self, state, path: Sized) -> PathExecutionResult:
        """
        Execute the given CFA path. NOTE: the passed states may be modified.

        All error and killed states met during the execution are counted
        as early terminated unless they are generated _after_ reaching
        the last location on the path. That is, the error states
        are those generated by annotations that follow the last location
        on the path.

        The method does not take into account whether the last
        location is error or not. This must be handled in the top-level code.
        I.e., if the last location is error location, then the result.ready
        states are in fact error states (those that reach the error location
        and pass the annotations of this location).

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

        pathlen = len(path)
        assert all(
            map(lambda s: isinstance(s, LazySEState), states)
        ), "Wrong state type"
        for idx in range(pathlen):
            edge = edges[idx]
            dbgv(f"vv ----- Edge {edge} ----- vv", verbose_lvl=3)
            states, nonready = self._execute_edge(states, edge)
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

        result.ready = states or None
        result.early = earlytermstates or None

        assert result.check(), "The states were partitioned incorrectly"
        return result

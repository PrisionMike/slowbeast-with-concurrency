from slowbeast.symexe.symbolicexecution import SEOptions
from slowbeast.symexe.executionstate import SEState
from slowbeast.util.debugging import print_stderr, print_stdout, dbg

from slowbeast.kindse.annotatedcfg import CFG
from slowbeast.kindse.naive.naivekindse import (
    KindSymbolicExecutor as BasicKindSymbolicExecutor,
)
from slowbeast.kindse.naive.naivekindse import Result, KindSeOptions
from slowbeast.kindse.naive.inductionpath import InductionPath

from copy import copy


class KindSymbolicExecutor(BasicKindSymbolicExecutor):
    def __init__(self, prog, ohandler=None, opts=KindSeOptions()):
        super(KindSymbolicExecutor, self).__init__(prog, opts)

        self.cfgs = {}
        self._infeasibleSuffixes = []

    def getCFG(self, F):
        return self.cfgs.setdefault(F, CFG(F))

    def hasInfeasibleSuffix(self, path):
        for p in self._infeasibleSuffixes:
            if path.getPath().endswith(p):
                return True
        return False

    def executePath(self, path):
        print_stdout("Executing path: {0}".format(path), color="ORANGE")
        ready, notready = self.getIndExecutor().executePath(
            path.getState(), path.getPath()
        )
        return ready, notready

    def extendIndPath(self, path):
        newpaths = []
        found_err = False

        for p in path.extend():
            if not p.reachesAssert():
                newpaths.append(p)
                continue

            if self.hasInfeasibleSuffix(p):
                # FIXME: this works only for "assert False" as it is in its own
                # block...
                dbg("Skipping path with infeasible suffix: {0}".format(p))
                continue

            # this path may reach an assert
            # so we must really execute it and get those
            # states that do no violate the assert
            ready, notready = self.executePath(p)

            newpaths += [InductionPath(r) for r in ready]

            if len(notready) == 0 and len(ready) == 0:
                self._infeasibleSuffixes.append(p.getPath())

            for ns in notready:
                if ns.hasError():
                    found_err = True
                    dbg(
                        "Hit error state in induction check: {0}: {1}, {2}".format(
                            ns.getID(), ns.pc, ns.getError()
                        ),
                        color="PURPLE",
                    )
                if ns.wasKilled():
                    print_stderr(
                        ns.getStatusDetail(), prefix="KILLED STATE: ", color="WINE"
                    )
                    return [], Result.UNKNOWN

        return newpaths, Result.UNSAFE if found_err else Result.SAFE

    def extendPaths(self, ind):
        found_err = False
        newpaths = []
        for path in ind:
            tmp, f_err = self.extendIndPath(path)
            if f_err == Result.UNKNOWN:
                return [], Result.UNKNOWN
            newpaths += tmp
            found_err |= f_err == Result.UNSAFE

        return newpaths, Result.UNSAFE if found_err else Result.SAFE

    def extendInd(self):
        pass  # we do all the work in checkInd

    def checkInd(self):
        self.ind, safe = self.extendPaths(self.ind)
        return safe

    def initializeInduction(self):
        cfg = self.getCFG(self.getProgram().getEntry())
        ind, done = super(KindSymbolicExecutor, self).initializeInduction()
        if done:
            return [], True
        # we do the first extension here, so that we can do the rest of the
        # work in checkInd and do not execute the paths repeatedly
        return self.extendPaths([InductionPath(cfg, s) for s in ind])

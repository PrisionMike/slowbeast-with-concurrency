from .. symexe.symbolicexecution import SymbolicExecutor, SEOptions
from .. symexe.executor import Executor as SExecutor
from .. symexe.memory import LazySymbolicMemoryModel
from .. util.debugging import print_stderr, print_stdout, dbg


class Result:
    UNKNOWN = 0
    SAFE = 1
    UNSAFE = 2

class KindSeOptions(SEOptions):
    __slots__ = ['step']

    def __init__(self, opts=None, step=-1):
        super(KindSeOptions, self).__init__(opts)
        self.step = step


class KindSymbolicExecutor(SymbolicExecutor):
    def __init__(
            self,
            prog,
            testgen=None,
            opts=KindSeOptions()):
        super(
            KindSymbolicExecutor, self).__init__(P=prog, testgen=testgen, opts=opts)

        # the executor for induction checks -- we need lazy memory access
        memorymodel = LazySymbolicMemoryModel(opts, self.getSolver())
        self.indexecutor = SExecutor(self.getSolver(), opts, memorymodel)
        dbg("Forbidding calls in induction step for now with k-induction")
        self.indexecutor.forbidCalls()

    def getIndExecutor(self):
        return self.indexecutor

    def extendBase(self):
        states = self.getExecutor().executeTillBranch(self.base)
        self.base = []
        for ns in states:
            if ns.hasError():
                print_stderr(
                    "{0}: {1}, {2}".format(
                        ns.getID(),
                        ns.pc,
                        ns.getError()),
                    color='RED')
                self.stats.errors += 1
                self.stats.paths += 1
                return Result.UNSAFE
            elif ns.isReady():
                self.base.append(ns)
            elif ns.isTerminated():
                print_stderr(ns.getError(), color='BROWN')
                self.stats.paths += 1
                self.stats.terminated_paths += 1
            elif ns.wasKilled():
                self.stats.paths += 1
                self.stats.killed_paths += 1
                print_stderr(
                    ns.getStatusDetail(),
                    prefix='KILLED STATE: ',
                    color='WINE')
                return Result.UNKNOWN
            else:
                assert ns.exited()
                self.stats.paths += 1
                self.stats.exited_paths += 1

        if not self.base:
            # no ready states -> we searched all the paths
            return Result.SAFE

        return None

    def extendInd(self):
        states = self.indexecutor.executeTillBranch(self.ind)

        self.ind = []
        found_err = False
        for ns in states:
            if ns.hasError():
                found_err = True
                dbg("Hit error state while building IS assumptions: {0}: {1}, {2}".format(
                    ns.getID(), ns.pc, ns.getError()), color="PURPLE")
            elif ns.isReady():
                self.ind.append(ns)
            elif ns.isTerminated():
                print_stderr(ns.getError(), color='BROWN')
            elif ns.wasKilled():
                print_stderr(
                    ns.getStatusDetail(),
                    prefix='KILLED STATE: ',
                    color='WINE')
                return Result.UNKNOWN
            else:
                assert ns.exited()

        return Result.UNSAFE if found_err else Result.SAFE

    def checkInd(self):
        frontier = [s.copy() for s in self.ind]
        states = self.indexecutor.executeTillBranch(frontier)

        has_error = False
        for ns in states:
            if ns.hasError():
                has_error = True
                dbg("Induction check hit error state: {0}: {1}, {2}".format(
                    ns.getID(), ns.pc, ns.getError()),
                    color="PURPLE")
                break
            elif ns.wasKilled():
                print_stderr(
                    ns.getStatusDetail(),
                    prefix='KILLED STATE: ',
                    color='WINE')
                return Result.UNKNOWN

        return Result.UNSAFE if has_error else Result.SAFE

    def initializeInduction(self):
        ind = []
        bblocks = self.getProgram().getEntry().getBBlocks()
        executor = self.indexecutor
        entry = self.getProgram().getEntry()
        append = ind.append
        for b in bblocks:
            s = executor.createState()
            s.pushCall(None, entry)
            s.pc = b.first()
            append(s)
        return ind, False

    def run(self):
        self.prepare()

        dbg("Performing the k-ind algorithm only for the main function",
            color="ORANGE")

        k = 1
        self.base = self.states  # start from the initial states
        self.ind, safe = self.initializeInduction()

        if safe:
            print_stdout("Found no error state!", color='GREEN')
            return 0

        while True:
            print_stdout("-- starting iteration {0} --".format(k))

            dbg("Extending base".format(k), color="BLUE")
            r = self.extendBase()
            if r == Result.UNSAFE:
                dbg("Error found.", color='RED')
                return 1
            elif r is Result.SAFE:
                print_stdout("We searched the whole program!", color='GREEN')
                return 0
            elif r is Result.UNKNOWN:
                print_stdout("Hit a problem, giving up.", color='ORANGE')
                return 1

            dbg("Extending induction step".format(k), color="BLUE")
            r = self.extendInd()
            if r == Result.SAFE:
                print_stdout("Did not hit any possible error while building "
                             "induction step!".format(k),
                             color="GREEN")
                return 0
            elif r is Result.UNKNOWN:
                print_stdout("Hit a problem, giving up.", color='ORANGE')
                return 1

            dbg("Checking induction step".format(k), color="BLUE")
            r = self.checkInd()
            if r == Result.SAFE:
                print_stdout("Induction step succeeded!", color='GREEN')
                return 0
            elif r is Result.UNKNOWN:
                print_stdout("Hit a problem, giving up.", color='ORANGE')
                return 1

            k += 1

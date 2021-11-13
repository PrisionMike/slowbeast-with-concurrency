from slowbeast.symexe.executionstate import SEState as ExecutionState
from slowbeast.symexe.symbolicexecution import SymbolicExecutor, SEOptions, SExecutor
from slowbeast.bse.bse import report_state
from slowbeast.bse.bself import BSELF, BSELFOptions, BSELFChecker
from slowbeast.cfkind.naive.naivekindse import Result
from slowbeast.util.debugging import print_stdout
from slowbeast.symexe.statesset import intersection

from slowbeast.cfkind.relations import get_var_cmp_relations

class SEState(ExecutionState):
    """
    Execution state of forward symbolic execution in BSELFF.
    It is exactly the same as the parent class, but it also
    computes the number of hits to a particular loop headers.
    """

    __slots__ = "_loc_visits"

    def __init__(self, executor=None, pc=None, m=None, solver=None, constraints=None):
        super().__init__(executor, pc, m, solver, constraints)
        self._loc_visits = {}

    def _copy_to(self, new):
        super()._copy_to(new)
        # FIXME: use COW
        new._loc_visits = self._loc_visits.copy()

    def visited(self, inst):
        n = self._loc_visits.setdefault(inst, 0)
        self._loc_visits[inst] = n + 1

    def num_visits(self, inst=None):
        if inst is None:
            inst = self.pc
        return self._loc_visits.get(inst)


class Executor(SExecutor):
    def create_state(self, pc=None, m=None):
        if m is None:
            m = self.getMemoryModel().create_memory()
        s = SEState(self, pc, m, self.solver)
        assert not s.constraints(), "the state is not clean"
        return s


class BSELFFSymbolicExecutor(SymbolicExecutor):
    def __init__(
            self, P, ohandler=None, opts=SEOptions(), executor=None, ExecutorClass=Executor, programstructure=None, fwdstates=None
    ):
        super().__init__(P, ohandler, opts, executor, ExecutorClass)
        self.programstructure = programstructure
        self._loop_headers = {loc.elem()[0] : loc for loc in self.programstructure.get_loop_headers()}
        self._covered_insts = set()
        self.forward_states = fwdstates

    def is_loop_header(self, inst):
        return inst in self._loop_headers

    def getNextState(self):
        states = self.states
        if not states:
            return None

        none_num = 0
        state_idx = None
        some_state_idx = None
        covered = self._covered_insts
        for idx in range(len(states)):
            state = states[idx]
            if state is None:
                none_num += 1
                continue
            if some_state_idx is None:
                some_state_idx = idx
            if state.pc not in covered:
                state_idx = idx
                break

        if state_idx is None:
            state_idx = some_state_idx
        if state_idx is None:
            assert all(map(lambda x: x is None, states))
            return None

        assert state_idx is not None
        state = states[state_idx]
        states[state_idx] = None

        # don't care about the +1 from prev line...
        if none_num > 20 and (none_num / len(states)) >= 0.5:
            self.states = [s for s in states if s is not None]
        return state

    def handleNewState(self, s):
        pc = s.pc
        self._covered_insts.add(pc)

        if s.is_ready() and self.is_loop_header(pc):
            s.visited(pc)
            self._register_loop_states(s)
        super().handleNewState(s)

    def _register_loop_states(self, state):
        n = state.num_visits()
        assert n > 0, "Bug in counting visits"
        states = self.forward_states.setdefault(state.pc, [])
        # if we have a state that visited state.pc n times,
        # we must have visited it also k times for all k < n
        assert len(states) != 0 or n == 1, self.forward_states
        assert len(states) >= n - 1, self.forward_states
        if len(states) == n - 1:
            states.append([state.copy()])
        else:
            assert len(states) >= n
            states[n - 1].append(state.copy())

       #S = self.executor().create_states_set(state)
       #loc = self._loop_headers[state.pc]
       #A, rels, states = self.forward_states.setdefault(loc, (self.executor().create_states_set(), set(), []))
       #cur_rels = set()
       #for rel in (r for r in get_var_cmp_relations(state, A) if r not in rels):
       #    if rel.get_cannonical().is_concrete(): # True
       #        continue
       #    rels.add(rel)
       #    cur_rels.add(rel)
       #    print('rel', rel)
       #    A.add(S)
       #states.append((state, rels))
       #print(states)
       #print(A)


class BSELFF(BSELF):
    """
    The main class for BSELFF (BSELF with forward analysis)
    """

    def __init__(self, prog, ohandler=None, opts=BSELFOptions()):
        print("BSELF^2")
        super().__init__(prog, ohandler, opts)
        self.forward_states = {}
        # self.create_set = self.ind_executor().create_states_set


    def run(self):
        se = BSELFFSymbolicExecutor(self.program, self.ohandler, self.options,
                                    programstructure=self.programstructure,
                                    fwdstates=self.forward_states)
        se.prepare()
        se_checkers = [se]

        bself_checkers = []
        for loc, A in self._get_possible_errors():
            print_stdout(f"Checking possible error: {A.expr()} @ {loc}", color="white")
            checker = BSELFChecker(
                loc,
                A,
                self.program,
                self.programstructure,
                self.options,
                invariants=self.invariants,
            )
            checker.init_checker()
            bself_checkers.append(checker)

        while True:
            for checker in se_checkers:
                checker.do_step()
                # forward SE found an error
                if checker.stats.errors > 0:
                    return Result.UNSAFE
                # forward SE searched whole program and found not error
                if not checker.states and checker.stats.killed_paths == 0:
                    return Result.SAFE

            bself_has_unknown = False
            remove_checkers = []
            for checker in bself_checkers:
                continue
                result, states = checker.do_step()
                if result is None:
                    continue
                self.stats.add(checker.stats)
                if result is Result.UNSAFE:
                    # FIXME: report the error from bsecontext
                    print_stdout(
                        f"{states.get_id()}: [assertion error]: {loc} reachable.",
                        color="redul",
                    )
                    print_stdout(str(states), color="wine")
                    print_stdout("Error found.", color="redul")
                    self.stats.errors += 1
                    return result
                if result is Result.SAFE:
                    print_stdout(
                        f"Error condition {A.expr()} at {loc} is safe!.", color="green"
                    )
                    remove_checkers.append(checker)
                elif result is Result.UNKNOWN:
                    print_stdout(f"Checking {A} at {loc} was unsuccessful.", color="yellow")
                    bself_has_unknown = True
                    assert checker.problematic_states, "Unknown with no problematic paths?"
                    for p in checker.problematic_states:
                        report_state(self.stats, p)

            for c in remove_checkers:
                bself_checkers.remove(c)
            if not bself_checkers:
                if bself_has_unknown:
                    print_stdout("Failed deciding the result.", color="orangeul")
                    return Result.UNKNOWN

                print_stdout("No error found.", color="greenul")
                ohandler = self.ohandler
                if ohandler:
                    ohandler.testgen.generate_proof(self)
                return Result.SAFE
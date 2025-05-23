from slowbeast.analysis.programstructure import ProgramStructure
from slowbeast.cfkind.naive.naivekindse import Result
from slowbeast.symexe.annotations import AssertAnnotation
from slowbeast.symexe.interpreter import SEStats
from slowbeast.util.debugging import (
    print_stdout,
    print_stderr,
    dbg,
)
from .bse import (
    report_state,
)
from .bselfchecker import BSELFChecker
from .options import BSELFOptions
from ..core.errors import MemError
from ..ir.instruction import Assert
from ..solvers.symcrete import global_expr_mgr


class BSELF:
    """
    The main class for BSE and BSELF (BSE is a BSELF without loop folding)
    that divides and conquers the tasks.
    """

    def __init__(
        self, prog, ohandler=None, opts: BSELFOptions = BSELFOptions()
    ) -> None:
        assert isinstance(opts, BSELFOptions), opts
        self.program = prog
        self.ohandler = ohandler
        self.options = opts

        if ohandler:
            self.new_output_file = self.ohandler.new_output_file
        else:
            from slowbeast.util.debugging import new_output_file

            self.new_output_file = new_output_file

        programstructure = ProgramStructure(prog, self.new_output_file)
        self.get_cfa = programstructure.cfas.get
        self.programstructure = programstructure

        self.stats = SEStats()

        self.invariants = {}
        self.reachable_states = {}

    def _get_possible_errors(self):
        EM = global_expr_mgr()
        for F in self.programstructure.callgraph.funs():
            if F.is_undefined():
                continue

            cfa = self.get_cfa(F)
            locs = cfa.locations()
            iserr = cfa.is_err

            for l in locs:
                if iserr(l):
                    yield l, AssertAnnotation(EM.get_false(), {}, EM)

    def create_checker(self, *args, **kwargs):
        return BSELFChecker(*args, **kwargs)

    def run(self) -> int:
        has_unknown = False
        for loc, A in self._get_possible_errors():
            print_stdout(f"Checking possible error: {A.expr()} @ {loc}", color="white")
            checker = self.create_checker(
                loc,
                A,
                self.program,
                self.programstructure,
                self.options,
                invariants=self.invariants,
                reachable_states=self.reachable_states,
            )
            result, state = checker.check()
            if result is Result.UNSAFE and state.memory.input_reads():
                dbg("Unmatched input reads found: {state.memory.input_reads()}")
                state.set_error(
                    MemError(MemError.UNINIT_READ, "Read of uninitialized byte")
                )
                checker.problematic_states.append(state)
                result = Result.UNKNOWN

            self.stats.add(checker.stats)
            if result is Result.UNSAFE:
                # FIXME: report the error from bsecontext
                loc_elem = loc.elem()
                msg = ""
                if loc_elem and isinstance(loc_elem, Assert):
                    msg = f"({loc_elem.msg()})"

                dbgloc = loc_elem.get_metadata("dbgloc")
                if dbgloc:
                    print_stderr(
                        f"[{state.get_id()}] {dbgloc[0]}:{dbgloc[1]}:{dbgloc[2]}: [assertion error]: {loc} reachable {msg}.",
                        color="redul",
                    )
                else:
                    print_stderr(
                        f"{state.get_id()}: [assertion error]: {loc} reachable {msg}.",
                        color="redul",
                    )

                print_stdout(str(state), color="wine")
                print_stdout("Error found.", color="redul")
                self.stats.errors += 1
                if self.ohandler:
                    self.ohandler.testgen.process_state(state)
                return result
            if result is Result.SAFE:
                print_stdout(
                    f"Error condition {A.expr()} at {loc} is safe!.", color="green"
                )
            elif result is Result.UNKNOWN:
                print_stdout(f"Checking {A} at {loc} was unsuccessful.", color="yellow")
                has_unknown = True
                assert checker.problematic_states, "Unknown with no problematic paths?"
                for p in checker.problematic_states:
                    report_state(self.stats, p)

        if has_unknown:
            print_stdout("Failed deciding the result.", color="orangeul")
            return Result.UNKNOWN

        print_stdout("No error found.", color="greenul")
        ohandler = self.ohandler
        if ohandler:
            ohandler.testgen.generate_proof(self)
        return Result.SAFE

from slowbeast.ir.instruction import (
    Alloc,
    Assume,
    Assert,
    Cmp,
    Print,
    Abs,
    FpOp,
    Cast,
    BinaryOperation,
    Extend,
    Load,
)
from slowbeast.ir.types import PointerType, type_mgr
from slowbeast.util.debugging import print_stderr
from .utils import get_llvm_operands, type_size_in_bits, to_float_ty, get_sb_type
from ...domains.concrete import ConstantFalse, ConcreteDomain
from ...domains.concrete_floats import ConcreteFloat

concrete_value = ConcreteDomain.get_value

# FIXME: turn to a dict with separate handlers
special_functions = [
    "llvm.fabs.f32",
    "llvm.fabs.f64",
    "llvm.fmuladd.f32",
    "llvm.fmuladd.f64",
    "llvm.minnum.f32",
    "llvm.minnum.f64",
    "llvm.maxnum.f32",
    "llvm.maxnum.f64",
    "llvm.round.f32",
    "llvm.round.f64",
    "llvm.floor.f32",
    "llvm.floor.f64",
    "llvm.ceil.f32",
    "llvm.ceil.f64",
    "llvm.trunc.f32",
    "llvm.trunc.f64",
    "abs",
    "sqrt",
    "sqrtf",
    "sqrtl",
    "fdim",
    "fesetround",
    "_setjmp",
    "setjmp",
    "longjmp",
    "nan",
    "erf",
    "erff",
    "erfl",
    "sin",
    "sinf",
    "sinl",
    "cos",
    "cosf",
    "cosl",
    "exp",
    "expf",
    "expl",
    "expm1",
    "expm1f",
    "expm1l",
    "log",
    "logf",
    "logl",
    "log1p",
    "log1pf",
    "log1pl",
    "tanh",
    "tanhf",
    "tanhl",
    "__isnan",
    "__isnanf",
    "__isnanl",
    "__isinf",
    "__isinff",
    "__isinfl",
    "__fpclassify",
    "__fpclassifyf",
    "__fpclassifyl",
    "__signbit",
    "__signbitf",
    "__signbitl",
    "malloc",
    "calloc",
    "__assert_fail",
    "__VERIFIER_error",
    "__VERIFIER_assume",
    "verifier.assume",
    "assume_abort_if_not",
    "__VERIFIER_silent_exit",
    "__slowbeast_print",
    "ldv_stop",
    "__errno_location",
    # kernel functions
    "printk",
    # string functions
    # "strcpy",
]

modelled_functions = ["__VERIFIER_assert"]


def try_model_function(parser, inst, fun, error_funs, to_check):
    """
    Return a pair R, S where R is the representant
    used for mapping of instructions and S is the sequence
    of instructions created
    """

    module = parser.llvmmodule
    no_overflow = to_check and "no-overflow" in to_check
    ignore_asserts = len(error_funs) > 0 or no_overflow
    if fun == "__VERIFIER_assert":
        if (
            len(error_funs) > 0
        ):  # if we look for some particular function, do not model this
            return None, None
        operands = get_llvm_operands(inst)
        cond = parser.operand(operands[0])
        optypes = [get_sb_type(module, op.type) for op in operands]
        C = Cmp(
            Cmp.NE,
            cond,
            concrete_value(0, type_size_in_bits(module, operands[0].type)),
            optypes,
        )
        if ignore_asserts:
            A = Assume(C)
        else:
            A = Assert(C)
        return A, [C, A]

    raise RuntimeError(f"Modelled function not handled: {fun}")


def create_special_fun(parser, inst, fun, error_funs, to_check):
    """
    Return a pair R, S where R is the representant
    used for mapping of instructions and S is the sequence
    of instructions created
    """

    def ops_and_types(inst, start, end):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(start, end)]
        types = [get_sb_type(module, operands[i].type) for i in range(start, end)]
        return ops, types

    module = parser.llvmmodule
    no_overflow = to_check and "no-overflow" in to_check
    ignore_asserts = len(error_funs) > 0 or no_overflow
    if fun in error_funs:
        A = Assert(ConstantFalse, "error function called!")
        return A, [A]
    elif fun == "__assert_fail":
        if ignore_asserts:
            # ignore assertions if error functions are given
            A = Assume(ConstantFalse)
        else:
            A = Assert(ConstantFalse, "assertion failed!")
        return A, [A]
    elif fun == "__VERIFIER_error":
        if ignore_asserts:
            # ignore assertions if error functions are given
            A = Assume(ConstantFalse)
        else:
            A = Assert(ConstantFalse, "__VERIFIER_error called!")
        return A, [A]
    elif fun in ("__VERIFIER_assume", "assume_abort_if_not", "verifier.assume"):
        operands = get_llvm_operands(inst)
        cond = parser.operand(operands[0])
        optypes = [get_sb_type(module, op.type) for op in operands]
        C = Cmp(
            Cmp.NE,
            cond,
            concrete_value(0, type_size_in_bits(module, operands[0].type)),
            optypes,
        )
        A = Assume(C)
        return A, [C, A]
    elif fun in ("__VERIFIER_silent_exit", "ldv_stop"):
        print_stderr("Assuming that ldv_stop is assume(false)...", color="orange")
        A = Assume(ConstantFalse)
        return A, [A]
    elif no_overflow and fun.startswith("__ubsan_handle"):
        A = Assert(ConstantFalse, "signed integer overflow")
        return A, [A]
    elif fun == "malloc":
        operands = get_llvm_operands(inst)
        assert (
            len(operands) == 2
        ), "Invalid malloc"  # (call has +1 operand for the function)
        size = parser.operand(operands[0])
        A = Alloc(size, on_heap=True)
        return A, [A]
    elif fun == "calloc":
        operands = get_llvm_operands(inst)
        assert (
            len(operands) == 3
        ), "Invalid calloc"  # (call has +1 operand for the function)
        size = BinaryOperation(
            BinaryOperation.MUL,
            parser.operand(operands[0]),
            parser.operand(operands[1]),
            [get_sb_type(module, operands[i].type) for i in (0, 1)],
        )
        A = Alloc(size, on_heap=True, zeroed=True)
        return A, [size, A]
    elif fun.startswith("llvm.fabs.") or fun == "abs":
        operands = get_llvm_operands(inst)
        val = parser.operand(operands[0])
        A = Abs(
            val,
            type_mgr().float_ty(type_size_in_bits(module, inst.type)),
            [get_sb_type(module, operands[0].type)],
        )
        return A, [A]
    elif fun.startswith("llvm.fmuladd."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 3)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 3)]
        MUL = BinaryOperation(BinaryOperation.MUL, ops[0], ops[1], types[:2])
        ADD = BinaryOperation(BinaryOperation.ADD, MUL, ops[2], [MUL.type(), types[2]])
        return ADD, [MUL, ADD]
    elif fun.startswith("llvm.minnum."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 2)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 2)]
        MIN = FpOp(FpOp.MIN, ops, types)
        return MIN, [MIN]
    elif fun.startswith("llvm.maxnum."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 2)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 2)]
        MAX = FpOp(FpOp.MAX, ops, types)
        return MAX, [MAX]
    elif fun.startswith("llvm.round."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 1)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 1)]
        ROUND = FpOp(FpOp.ROUND, ops, types)
        return ROUND, [ROUND]
    elif fun.startswith("llvm.floor."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 1)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 1)]
        fpop = FpOp(FpOp.FLOOR, ops, types)
        return fpop, [fpop]
    elif fun.startswith("llvm.ceil."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 1)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 1)]
        fpop = FpOp(FpOp.CEIL, ops, types)
        return fpop, [fpop]
    elif fun.startswith("llvm.trunc."):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 1)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 1)]
        fpop = FpOp(FpOp.TRUNC, ops, types)
        return fpop, [fpop]
    elif fun in ("sqrt", "sqrtf", "sqrtl"):
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 1)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 1)]
        SQRT = FpOp(FpOp.SQRT, ops, types)
        return SQRT, [SQRT]
    elif fun in ("__isinf", "__isinff", "__isinfl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.IS_INF, [val], [get_sb_type(module, operands[0].type)])
        P = Extend(
            O,
            type_size_in_bits(module, inst.type),
            True,  # unsigned
            [get_sb_type(module, operands[0].type)],
        )
        return P, [O, P]
    elif fun == "fdim":
        operands = get_llvm_operands(inst)
        ops = [parser.operand(operands[i]) for i in range(0, 2)]
        types = [get_sb_type(module, operands[i].type) for i in range(0, 2)]
        fpop = FpOp(FpOp.DIM, ops, types)
        return fpop, [fpop]
    elif fun in "nan":
        operands = get_llvm_operands(inst)
        I = Cast(
            ConcreteFloat("NaN", 64),
            type_mgr().float_ty(64),
            True,
            [get_sb_type(module, operands[0].type)],
        )
        return I, [I]
    elif fun in ("__isnan", "__isnanf", "__isnanfl", "__isnanl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.IS_NAN, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        P = Extend(
            O,
            type_size_in_bits(module, inst.type),
            True,  # unsigned
            [get_sb_type(module, operands[0].type)],
        )
        return P, [O, P]
    elif fun in ("__fpclassify", "__fpclassifyf", "__fpclassifyl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.FPCLASSIFY, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun in ("__signbit", "__signbitf", "__signbitl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.SIGNBIT, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun in ("erf", "erff", "erfl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.ERF, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun in ("sin", "sinf", "sinl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.SIN, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun in ("cos", "cosf", "cosl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.COS, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun in ("exp", "expf", "expl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.EXP, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun in ("log", "logf", "logl"):
        operands = get_llvm_operands(inst)
        val = to_float_ty(parser.operand(operands[0]))
        O = FpOp(FpOp.LOG, [val], [get_sb_type(module, operands[0].type)])
        # the functions return int
        return O, [O]
    elif fun == "__errno_location":
        errn = parser.get_or_create_errno()
        L = Load(errn, errn.type(), [type_mgr().pointer_ty()])
        return L, [L]
    elif fun == "printk":
        return None, []
    elif fun == "__slowbeast_print":
        P = Print(*[parser.operand(x) for x in get_llvm_operands(inst)[:-1]])
        return P, [P]
    # elif fun == "strcpy":
    #     operands = get_llvm_operands(inst)
    #     dest, src = [parser.operand(operands[i]) for i in range(2)]
    #     types = [get_sb_type(module, operands[i].type) for i in range(2)]
    #     assert all(type(_type) == PointerType() for _type in types)
    #     save = Alloc(dest, on_heap=False)
    #     index = 0
    #     while True:
    #         char = Load(src + index, type_mgr().char_ty(), [])

        
    elif fun in ("fesetround", "_setjmp", "setjmp", "longjmp"):
        raise NotImplementedError(f"{fun} is not supported yet")
    else:
        raise NotImplementedError(f"Unknown special function: {fun}")

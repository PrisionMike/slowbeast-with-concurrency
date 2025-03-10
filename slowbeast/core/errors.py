class Error:
    """
    Generic error type that represents an error in execution
    of program (e.g., assertion violation, out-of-bound access to memory,
    etc.)
    """

    __slots__ = "_type", "_descr"

    UNKNOWN = 0
    ASSERTION_FAIL = 1
    MEM_ERROR = 2
    NONTERMINATION = 3
    GENERIC = 33

    def __init__(self, t, d=None) -> None:
        self._type = t
        self._descr = d

    def type(self):
        return self._type

    def descr(self):
        return self._descr

    def is_memory_error(self):
        return self._type == Error.MEM_ERROR

    def is_assertion_fail(self):
        return self._type == Error.ASSERTION_FAIL

    def is_non_termination(self):
        return self._type == Error.NONTERMINATION

    def __repr__(self) -> str:
        ty = self._type
        if ty == Error.UNKNOWN:
            detail = "[unknown error]"
        elif ty == Error.ASSERTION_FAIL:
            detail = "[assertion error]"
        elif ty == Error.MEM_ERROR:
            detail = "[memory error]"
        elif ty == Error.NONTERMINATION:
            detail = "[non-termination]"
        elif ty == Error.GENERIC:
            detail = "[generic error]"
        else:
            raise RuntimeError("Invalid error type")
        return detail

    def __str__(self) -> str:
        if self._descr:
            return f"{self.__repr__()}: {self._descr}"
        return self.__repr__()


class AssertFailError(Error):
    def __init__(self, descr=None) -> None:
        super().__init__(Error.ASSERTION_FAIL, descr)


class NonTerminationError(Error):
    def __init__(self, descr=None) -> None:
        super().__init__(Error.NONTERMINATION, descr)


class GenericError(Error):
    def __init__(self, descr=None) -> None:
        super().__init__(Error.GENERIC, descr)


class MemError(Error):
    """
    Memory errors like invalid pointer dereference or out-of-bound
    access to memory.
    """

    __slots__ = "_memerr"

    OOB_ACCESS = 1
    UNINIT_READ = 2
    INVALID_OBJ = 3
    UNSUPPORTED = 4
    DATA_RACE = 5

    def __init__(self, t, descr=None) -> None:
        super(MemError, self).__init__(Error.MEM_ERROR, descr)
        self._memerr = t

    def is_uninit_read(self):
        return self._memerr == MemError.UNINIT_READ

    def is_oob_access(self):
        return self._memerr == MemError.OOB_ACCESS

    def is_invalid_obj_access(self):
        return self._memerr == MemError.INVALID_OBJ

    def is_unsupported(self):
        return self._memerr == MemError.UNSUPPORTED

    def is_data_race_error(self):
        return self._memerr == MemError.DATA_RACE

    def __repr__(self) -> str:
        err = self._memerr
        assert self.is_memory_error()
        if err == MemError.OOB_ACCESS:
            detail = "oob"
        elif err == MemError.UNINIT_READ:
            detail = "uninitialized read"
        elif err == MemError.INVALID_OBJ:
            detail = "invalid object"
        elif err == MemError.UNSUPPORTED:
            detail = "unsupported operation"
        elif err == MemError.DATA_RACE:
            detail = "Data Race detected"
        else:
            raise RuntimeError("Invalid memory error type")

        return "[memory error] - {1}".format(super(MemError, self).__repr__(), detail)

    def __str__(self) -> str:
        return f"{self.__repr__()} ({self.descr()})"

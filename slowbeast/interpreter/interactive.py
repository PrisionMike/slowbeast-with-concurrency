from ..util.debugging import dbg
from typing import Sized


class InteractiveHandler:
    def __init__(self, interpreter) -> None:
        self.interpreter = interpreter
        self._last_query = None
        self._stop_next_time = True
        self._break_inst = []
        self._break_pathid = []

    def _shouldSkip(self, s) -> bool:
        if self._stop_next_time:
            return False
        if s.get_id() in self._break_pathid:
            return False
        if s.pc.get_id() in self._break_inst:
            return False
        return True

    def prompt(self, s) -> None:
        """s = currently executed state
        newstates = states generated
        """
        try:
            self._prompt(s)
        except EOFError:
            print("Exiting...")
            exit(0)

    def _prompt(self, s) -> None:
        if self._shouldSkip(s):
            return

        self._stop_next_time = False

        print(f"Stopped before executing: ({s.get_id()}) {s.pc}")
        q = input("> ")
        if q == "":
            q = self._last_query
        while not self.handle(q, s):
            q = input("> ")

        self._last_query = q

    def handle(self, q, s) -> bool:
        """Return False for new prompt (the handling was unsuccessful)"""
        try:
            return self._handle(q, s)
        except KeyboardInterrupt:
            print("Interrupted")
            return False
        except Exception as e:
            print(f"An exception occured during handling '{q}'")
            print(str(e))
            return False
        return False

    def _handle(self, q, s) -> bool:
        dbg(f"query: {q}")
        query = q.split()
        if len(query) < 1:
            return False

        if query[0] in ["c", "continue"]:
            return True  # True = continute
        if query[0] in ["n", "s", "step", "next"]:
            self._stop_next_time = True
            return True
        if query[0] == "p":
            self.handle_print(query[1:], s)
        elif query[0] == "b":
            self.handle_break(query[1:])
        elif query[0] in ["l", "list"]:
            if len(query) == 1:
                i = s.pc
                n = 0
                while i and n < 5:
                    i.dump()
                    i = i.get_next_inst()
                    n += 1
            elif query[1] in ["b", "bblock", "block"]:
                s.pc.bblock().dump()
        else:
            print(f"Unknown query: {1}")
            print("FIXME: ... print help ...")
        return False

    def _getstate(self, i):
        for s in self.interpreter.get_states():
            if s.get_id() == i:
                return s
        return None

    def handle_break(self, query) -> None:
        if not query:
            print("Break on instructions: ", self._break_inst)
            print("Break on path ID: ", self._break_pathid)
        if query[0] in ["p", "path"]:
            self._break_pathid.append(int(query[1]))
            print("Break on path ID: ", self._break_pathid)
        elif query[0] in ["i", "inst", "instruction"]:
            self._break_inst.append(int(query[1]))
            print("Break on instructions: ", self._break_inst)
        # elif query[0] in ['s', 'state']: # NOTE: will not work, states do not
        # have any unique id

    def handle_print(self, query: Sized, state) -> None:
        if not query:
            raise RuntimeError("Invalid arguments to print")
        if query[0] == "states":
            print([x.get_id() for x in self.interpreter.get_states()])
        elif query[0] in ["new", "newstates"]:
            print([x.get_id() for x in self.interpreter.get_states()])
        elif query[0] in ["s", "state"]:
            if len(query) == 1:
                assert state, "No current state"
                s = state
            else:
                s = self._getstate(int(query[1]))
            if s:
                s.dump()
            else:
                print("No such a state")
        # elif query[0].startswith('x'):
        # NOTE: need to get the Instruction first
        # if val is None:
        #    print("No such a value")
        # else:
        #    print("{0} -> {1}".format(query[0], val))
        else:
            raise NotImplementedError("Invalid print command")

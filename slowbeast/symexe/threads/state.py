from __future__ import annotations
from sys import stdout
from typing import TextIO, Self

from slowbeast.core.callstack import CallStack

# from slowbeast.core.errors import GenericError
from slowbeast.ir.instruction import ThreadJoin, Store, Load
from slowbeast.symexe.state import SEState as BaseState, Thread, Event
from slowbeast.symexe.threads.trace import Action

# from slowbeast.symexe.threads.iexecutor import IExecutor
from slowbeast.symexe.threads.trace import Trace


class TSEState(BaseState):
    """
    TODO: Deprecate all things which shouldn't be owned by
    the state but should only be owned by a specific thread:
    (state.pc, _current_thread)
    """

    __slots__ = (
        "_threads",
        "_current_thread",
        "_exited_threads",
        "_wait_join",
        "_wait_mutex",
        "_mutexes",
        "_last_tid",
        "conflicts",
        "immediate_conflicts",
        "data_race",
        "trace",
        "bakctrack",
        # "terminal_action",
    )

    def __init__(
        self,
        executor=None,
        pc=None,
        m=None,
        solver=None,
        constraints=None,
    ) -> None:
        super().__init__(executor, pc, m, solver, constraints)
        self._last_tid = 0
        self._current_thread = 0
        # [Thread(0, pc, self.memory.get_cs() if m else None)]
        if m:
            self._threads = {0: Thread(0, pc, self.memory.get_cs())}
        else:
            None
        self._wait_join = {}
        self._exited_threads = {}
        self._mutexes = {}
        self._wait_mutex = {}
        self.trace: Trace = Trace()

    def _thread_idx(self, thr: Thread) -> int:
        """Return ID of a given thread. Thread's own ID"""
        for idx in self._threads:
            if self._threads[idx] == thr:
                return idx
        else:
            return None

    def _copy_to(self, new: Self) -> None:
        # assert not self.is_bot, "Don't copy the bottom state"
        super()._copy_to(new)
        new._threads = {id: thr.copy() for id, thr in self._threads.items()}
        new._wait_join = self._wait_join.copy()
        new._exited_threads = self._exited_threads.copy()
        new._last_tid = self._last_tid
        new._current_thread = self._current_thread
        new._mutexes = self._mutexes.copy()
        new._wait_mutex = {mtx: W.copy() for mtx, W in self._wait_mutex.items() if W}
        new.trace = self.trace

    # def lazy_eval(self, v: Union[Alloc, GlobalVariable]):
    #     value = self.try_eval(v)
    #     if value is None:
    #         vtype = v.type()
    #         if vtype.is_pointer():
    #             if isinstance(
    #                 v, (Alloc, GlobalVariable)
    #             ):  # FIXME: this is hack, do it generally for pointers
    #                 self.executor().memorymodel.lazy_allocate(self, v)
    #                 return self.try_eval(v)
    #             name = f"unknown_ptr_{v.as_value()}"
    #         else:
    #             name = f"unknown_{v.as_value()}"
    #         value = self.solver().symbolic_value(name, v.type())
    #         ldbgv(
    #             "Created new nondet value {0} = {1}",
    #             (v.as_value(), value),
    #             color="dark_blue",
    #         )
    #         self.set(v, value)
    #         self.create_nondet(v, value)
    #     return value

    def sync_pc(self) -> None:
        if self._threads:
            self._threads[self._current_thread].pc = self.pc

    def sync_cs(self) -> None:
        """Synchronise callstack"""
        if self._threads:
            self.thread().set_cs(self.memory.get_cs())

    def add_event(self) -> None:
        self._events.append(Event(self))

    def get_last_event(self):
        if self._events:
            return self._events[-1]
        return None

    def events(self):
        return self._events

    def schedule(self, idx) -> None:
        if self._current_thread == idx:
            return

        # schedule new thread
        thr: Thread = self.thread(idx)
        assert thr, self._threads
        self.pc = thr.pc
        self.memory.set_cs(thr.get_cs())
        self._current_thread = idx

    def add_thread(self, thread_fn, pc, args) -> Thread:
        self._last_tid += 1
        cs = CallStack()
        cs.push_call(None, thread_fn, args)
        t = Thread(self._last_tid, pc, cs)
        assert not t.is_paused()
        self._threads[self._last_tid] = t
        # self._trace.append(f"add thread {t.get_id()}")
        return t

    def current_thread(self) -> int:
        return self._current_thread

    def thread(self, idx=None) -> Thread:
        return self._threads[self._current_thread if idx is None else idx]

    def thread_ids(self):
        return self._threads.keys()

    def thread_id(self, idx=None):
        return self._threads[self._current_thread if idx is None else idx].get_id()

    def pause_thread(self, idx=None) -> None:
        self._threads[self._current_thread if idx is None else idx].pause()

    def unpause_thread(self, idx=None) -> None:
        self._threads[self._current_thread if idx is None else idx].unpause()

    def start_atomic(self, idx=None) -> None:
        assert not self._threads[
            self._current_thread if idx is None else idx
        ].in_atomic()
        self._threads[self._current_thread if idx is None else idx].set_atomic(True)

    def end_atomic(self, idx=None) -> None:
        assert self._threads[self._current_thread if idx is None else idx].in_atomic()
        self._threads[self._current_thread if idx is None else idx].set_atomic(False)

    def mutex_locked_by(self, mtx):
        return self._mutexes.get(mtx)

    def mutex_init(self, mtx) -> None:
        self._mutexes[mtx] = None

    def mutex_destroy(self, mtx) -> None:
        self._mutexes.pop(mtx)

    def has_mutex(self, mtx):
        return mtx in self._mutexes

    def mutex_lock(self, mtx, idx=None) -> None:
        tid = self.thread(self._current_thread if idx is None else idx).get_id()
        assert self.mutex_locked_by(mtx) is None, "Locking locked mutex"
        self._mutexes[mtx] = tid

    def mutex_unlock(self, mtx, idx=None) -> None:
        assert (
            self.mutex_locked_by(mtx)
            == self.thread(self._current_thread if idx is None else idx).get_id()
        ), "Unlocking wrong mutex"
        self._mutexes[mtx] = None
        tidx = self._thread_idx
        unpause = self.unpause_thread
        W = self._wait_mutex.get(mtx)
        if W is not None:
            for tid in W:
                unpause(tidx(tid))
            self._wait_mutex[mtx] = set()

    def mutex_wait(self, mtx, idx=None) -> None:
        "Thread idx waits for mutex mtx"
        tid = self._current_thread if idx is None else idx
        assert self.mutex_locked_by(mtx) is not None, "Waiting for unlocked mutex"
        self.pause_thread(idx)
        self._wait_mutex.setdefault(mtx, set()).add(tid)

    def exit_thread(self, retval, tid=None) -> None:
        """Exit thread and wait for join (if not detached)"""
        tid = self._current_thread if tid is None else tid
        assert tid not in self._exited_threads
        self._exited_threads[tid] = retval
        self.remove_thread(tid)

        if tid in self._wait_join:
            waiting_thread_ids = self._wait_join.pop(tid)
            for waitidx in waiting_thread_ids:
                assert self.thread(waitidx).is_paused(), self._wait_join
                self.unpause_thread(waitidx)
                t = self.thread(waitidx)
                # pass the return value
                assert isinstance(t.pc, ThreadJoin), t
                t.get_cs().set(t.pc, retval)
                t.pc = t.pc.get_next_inst()

    def join_threads(self, tid, totid: Thread | None = None) -> None:
        """
        tid: id of the thread that joins
        totid: id of the thread to which to join (None means the current thread)
        """
        if tid in self._exited_threads:
            # pass the return value
            retval = self._exited_threads.pop(tid)
            self.thread(totid).get_cs().set(self.thread(totid).pc, retval)
            self.thread(totid).pc = self.thread(totid).pc.get_next_inst()
            return

        toidx = (
            self._current_thread
            if totid is None
            else self._thread_idx(self.thread(totid))
        )
        if tid not in self._wait_join:
            self._wait_join[tid] = []
        if toidx not in self._wait_join[tid]:
            self._wait_join[tid].append(toidx)
        self.pause_thread(toidx)

    def remove_thread(self, idx=None) -> None:
        self._threads.pop(self._current_thread if idx is None else idx)
        if self._threads:
            self.pc = self._threads[0].pc
            self.memory.set_cs(self._threads[0].get_cs())
            self._current_thread = 0

        if self.num_threads() == 0:
            self.set_exited(0)

    def num_threads(self) -> int:
        return len(self._threads)

    # def race_condition_possible(self) -> bool:
    #     """Sets `race_alert` flag if more than 1 thread is active."""
    #     sleeping_threads = [thread.is_paused() for thread in self._threads.values()]
    #     if all(sleeping_threads):
    #         self.set_error(GenericError("Deadlock detected"))
    #         return False
    #     self._race_alert = sleeping_threads.count(False) > 1
    #     if not self._race_alert:
    #         self._tainted_locations = []
    #     return self._race_alert

    def threads(self) -> iter:
        return self._threads.values()

    def dump(self, stream: TextIO = stdout) -> None:
        super().dump(stream)
        write = stream.write
        write(" -- Threads --\n")
        for idx, t in enumerate(self._threads):
            write(f"  {idx}: {t}\n")

        write(f" -- Exited threads waiting for join: {self._exited_threads}\n")
        write(f" -- Threads waiting in join: {self._wait_join}\n")
        write(f" -- Mutexes (locked by): {self._mutexes}\n")
        write(f" -- Threads waiting for mutexes: {self._wait_mutex}\n")
        write(" -- Events --\n")
        for it in self._events:
            write(str(it) + "\n")

    def exec_thread(self, thread: int) -> set[Self]:
        output_states = self._executor.execute_single_thread(self, thread)
        return output_states

    def thread_to_action(self, tid: int) -> Action | None:
        """Convert an active thread pc instruction to an action.
        Return None if such an action cannot be added (thread paused, etc.)"""
        if (
            tid in self.thread_ids()
            and not self.thread(tid).is_paused()
            and not self.thread(tid).is_detached()
        ):
            assert self.thread(tid).pc, "Thread {tid} PC empty"
            return Action(tid, self.thread(tid).pc)
        else:
            return None

    def exec_trace(self, trace: Trace) -> list[Self]:
        """ASSUMES NON-TERMINAL PART OF THE TRACE BELONGS TO THE STATE ITSELF"""
        self.trace = trace
        return self.exec_thread(trace.terminal_thread())

    def check_data_race(self) -> None:
        write_locations = set()
        read_locations = set()
        for t in self.threads():
            if not (t.is_paused() or t.is_detached()):
                if isinstance(t.pc, Store):
                    write_locations.add(t.pc.pointer_operand())
                elif isinstance(t.pc, Load):
                    read_locations.add(t.pc.pointer_operand())
        if write_locations.intersection(read_locations):
            err = MemError(MemError.DATA_RACE, "DATA RACE DETECTED")
            self.set_error(err)
            sys.exit(1)

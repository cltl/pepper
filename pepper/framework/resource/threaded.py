import threading
from collections import defaultdict
from contextlib import contextmanager

from pepper import logger
from pepper.framework.di_container import singleton
from .api import ReadLock, WriteLock, ResourceManager, ResourceContainer


class ThreadedResourceContainer(ResourceContainer):
    @property
    @singleton
    def resource_manager(self):
        return ThreadedResourceManager()


class ThreadedResourceManager(ResourceManager):
    def __init__(self):
        self._registry_lock = threading.Lock()
        self._locks = {}
        self._resources = {}
        self._resource_events = defaultdict(list)

    def get_lock(self, name, blocking=True, timeout=-1):
        return self.get_write_lock(name, blocking, timeout, writer_interrupts=True)

    def get_read_lock(self, name, blocking=True, timeout=-1):
        if blocking:
            self._await_resource(name, timeout)

        if name not in self._locks:
            self._init_lock(name, _RWLock)

        logger.debug("Retrieved read-lock for resource %s from thread %s", name, threading.current_thread().name)

        return ThreadedReadLock(self._locks[name], name)

    def get_write_lock(self, name, blocking=True, timeout=-1, writer_interrupts=False):
        if blocking:
            self._await_resource(name, timeout)

        if name not in self._locks:
            self._init_lock(name, _RWLock)

        logger.debug("Retrieved write-lock for resource %s from thread %s", name, threading.current_thread().name)

        return ThreadedWriteLock(self._locks[name], name, writer_interrupts=writer_interrupts)

    def provide_resource(self, name):
        with self._registry_lock:
            if not self.has_resource(name):
                self._resources[name] = True
                logger.info("Registered resource: %s from thread %s", name, threading.current_thread().name)
            else:
                raise ValueError("Resource already provided: " + name)

            if name in self._resource_events:
                [event.set() for event in self._resource_events[name]]
                del self._resource_events[name]

    def retract_resource(self, name, force=True, timeout=-1):
        with self._registry_lock:
            lock = self._acquire_lock(force, name, timeout)
            try:
                del self._resources[name]
                if name in self._locks:
                    del self._locks[name]
            finally:
                if lock:
                    lock.writer_release()

        logger.info("Unregistered resource: " + name)

    def _acquire_lock(self, force, name, timeout):
        if force or name not in self._locks:
            return None

        lock = self._locks[name]
        lock.writer_acquire(timeout=timeout)

        return lock

    @property
    def resources(self):
        return self._resources.viewkeys()

    def _init_lock(self, name, factory):
        with self._registry_lock:
            if name not in self._locks:
                self._locks[name]= factory()

    def _await_resource(self, name, timeout=-1):
        if self.has_resource(name):
            return

        event = None
        with self._registry_lock:
            if name not in self._resources:
                event = threading.Event()
                self._resource_events[name].append(event)

        if event:
            event.wait()


class ThreadedReadLock(ReadLock):
    def __init__(self, rw_lock, resource_name):
        # type: (_RWLock, str) -> None
        self._resource_name = resource_name
        self._rw_lock = rw_lock
        self._lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        if self._rw_lock.reader_acquire(blocking=blocking, timeout=timeout):
            self._lock.acquire()
            logger.debug("Acquired read-lock for resource %s from thread %s", self._resource_name, threading.current_thread().name)
            return True
        else:
            return False

    @property
    def locked(self):
        return self._lock.locked()

    def release(self):
        self._lock.release()
        self._rw_lock.reader_release()
        logger.debug("Released read-lock for resource %s from thread %s", self._resource_name, threading.current_thread().name)

    @property
    def interrupted(self):
        return self._rw_lock.reader_interrupted() and self._lock.locked()


class ThreadedWriteLock(WriteLock):
    def __init__(self, lock, resource_name, writer_interrupts=False):
        # type: (_RWLock, str, bool) -> None
        self._resource_name = resource_name
        self._writer_interrupts = writer_interrupts
        self._rw_lock = lock
        self._lock = threading.Lock()

    def acquire(self, blocking=True, timeout=-1):
        if self._rw_lock.writer_acquire(blocking=blocking, timeout=timeout):
            self._lock.acquire()
            logger.debug("Acquired write-lock for resource %s from thread %s", self._resource_name, threading.current_thread().name)
            return True
        else:
            return False

    @property
    def locked(self):
        return self._lock.locked()

    def release(self):
        self._lock.release()
        self._rw_lock.writer_release()
        logger.debug("Released write-lock for resource %s from thread %s", self._resource_name, threading.current_thread().name)

    @property
    def interrupted(self):
        return self._rw_lock.writer_interrupted(writer_interrupts=self._writer_interrupts) and self._lock.locked()


# Modified version of:
# Mateusz Kobos:
# http://code.activestate.com/recipes/577803-reader-writer-lock-with-priority-for-writers

class _RWLock(object):
    """Synchronization object used in a solution of so-called second
    readers-writers problem. In this problem, many readers can simultaneously
    access a share, and a writer has an exclusive access to this share.
    Additionally, the following constraints should be met:
    1) no reader should be kept waiting if the share is currently opened for
        reading unless a writer is also waiting for the share,
    2) no writer should be kept waiting for the share longer than absolutely
        necessary.

    The implementation is based on [1, secs. 4.2.2, 4.2.6, 4.2.7]
    with a modification -- adding an additional lock (C{self.__readers_queue})
    -- in accordance with [2].

    Sources:
    [1] A.B. Downey: "The little book of semaphores", Version 2.1.5, 2008
    [2] P.J. Courtois, F. Heymans, D.L. Parnas:
        "Concurrent Control with 'Readers' and 'Writers'",
        Communications of the ACM, 1971 (via [3])
    [3] http://en.wikipedia.org/wiki/Readers-writers_problem
    """

    def __init__(self):
        self.__read_switch = _LightSwitch("read")
        self.__write_switch = _LightSwitch("write")
        self.__block_readers = threading.Lock()
        self.__block_resource = threading.Lock()
        self.__readers_queue = threading.Lock()
        """A lock giving an even higher priority to the writer in certain
        cases (see [2] for a discussion)"""

    def reader_acquire(self, blocking=True, timeout=-1):
        # TODO 3.6: timeout=timeout
        with _acquire(self.__readers_queue, blocking) as acquired_queue, \
                _acquire(self.__block_readers, blocking) as acquired_block:
            if acquired_queue and acquired_block:
                return self.__read_switch.acquire(self.__block_resource, blocking=blocking, timeout=timeout)

        return False

    def reader_release(self):
        self.__read_switch.release(self.__block_resource)

    def writer_acquire(self, blocking=True, timeout=-1):
        switch_acquired = self.__write_switch.acquire(self.__block_readers, blocking=blocking, timeout=timeout)
        if switch_acquired:
            if self.__block_resource.acquire(blocking):
                return True
            else:
                self.__write_switch.release(self.__block_readers)

                return False
        else:
            return False

    def writer_release(self):
        self.__block_resource.release()
        self.__write_switch.release(self.__block_readers)

    def reader_interrupted(self):
        return self.__read_switch.is_on and self.__write_switch.is_acquired

    def writer_interrupted(self, writer_interrupts=False):
        readers_interrupted = self.__write_switch.is_on and self.__readers_queue.locked()

        if writer_interrupts:
            return readers_interrupted or self.__write_switch.interrupted

        return readers_interrupted


class _LightSwitch:
    """An auxiliary "light switch"-like object. The first thread turns on the
    "switch", the last one turns it off (see [1, sec. 4.2.2] for details)."""

    def __init__(self, name):
        self.name = name
        self.__acquired = 0
        self.__is_on = False
        self.__mutex = threading.Lock()

    def acquire(self, lock, blocking=True, timeout=-1):
        # TODO 3.6: timeout=timeout
        with _acquire(self.__mutex, blocking) as acquired_mutex:
            if acquired_mutex:
                self.__acquired += 1
                if self.__acquired == 1:
                    # TODO 3.6: timeout=timeout
                    if lock.acquire(blocking):
                        self.__is_on = True
                    else:
                        self.__acquired -= 1

                return self.__acquired > 0
            else:
                return False

    def release(self, lock):
        with self.__mutex:
            self.__acquired -= 1
            if self.__acquired == 0:
                self.__is_on = False
                lock.release()

    @property
    def interrupted(self):
        with _acquire(self.__mutex, blocking=False) as in_mutex:
            return not in_mutex or self.__acquired > 1

    @property
    def is_acquired(self):
        with _acquire(self.__mutex, blocking=False) as in_mutex:
            return not in_mutex or self.__acquired > 0

    @property
    def is_on(self):
        with _acquire(self.__mutex, blocking=False) as acquired:
            return not acquired or self.__is_on


@contextmanager
def _acquire(lock, blocking):
    result = lock.acquire(blocking)
    yield result
    if result:
        lock.release()

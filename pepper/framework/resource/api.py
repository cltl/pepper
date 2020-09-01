from contextlib import contextmanager

from typing import Iterable

from pepper.framework.di_container import DIContainer


class LockTimeoutError(Exception):
    """
    Raised if an operation runs into a timeout constraint.
    """
    pass


class ResourceContainer(DIContainer):
    """
    :class:`~pepper.framework.di_container.DIContainer` providing a :class:`.ResourceManager` instance.
    """
    @property
    def resource_manager(self):
        raise NotImplementedError()


class ResourceManager(object):
    """
    ResourceManager manages resources available in the system.

    Resources can be registered by name and different Locks can be obtained
    to synchronize access to the registered resources.
    """
    def get_lock(self, name, blocking=True, timeout=-1):
        # type: (str, bool, float) -> Lock
        """
        Obtain a :class:`Lock` for the given resource.

        Parameters
        ----------
        blocking : bool
            Block until the resource is available or return immediately
        timeout : float or None
            Wait at most the specified `timeout` in seconds until the resource
            is available if the specified timeout is positive, otherwise wait
            indefinitely.

        Returns
        -------
        :class:`Lock`
            The lock.
        """
        raise NotImplementedError()

    def get_read_lock(self, name, blocking=True, timeout=-1):
        # type: (str, bool, float) -> ReadLock
        """
        Obtain a :class:`ReadLock` for the given resource.

        Parameters
        ----------
        blocking : bool
            Block until the resource is available or return immediately
        timeout : float or None
            Wait at most the specified `timeout` in seconds until the resource
            is available if the specified timeout is positive, otherwise wait
            indefinitely.

        Returns
        -------
        :class:`Lock`
            The lock.
        """
        raise NotImplementedError()

    def get_write_lock(self, name, blocking=True, timeout=-1):
        # type: (str, bool, float) -> WriteLock
        """
        Obtain a :class:`WriteLock` for the given resource.

        Parameters
        ----------
        blocking : bool
            Block until the resource is available or return immediately
        timeout : float or None
            Wait at most the specified `timeout` in seconds until the resource
            is available if the specified timeout is positive, otherwise wait
            indefinitely.

        Returns
        -------
        :class:`Lock`
            The lock.
        """
        raise NotImplementedError()

    def provide_resource(self, name):
        # type: (str) -> None
        """
        Register the resource with the given `name`.

        Parameters
        ----------
        name : str
            The name of the resource.

        Raises
        ------
        :exception:ValueError
            if there is already a resource registered with the given name.
        """
        raise NotImplementedError()

    def retract_resource(self, name, force=False, timeout=-1):
        # type: (str, bool, float) -> None
        """
        Unregister the resource with the given `name`.

        Parameters
        ----------
        name : str
            The name of the resource.
        force : bool
            Immediately retract the resource or block until all users released
            the released the resource.
        timeout : float or None
            Wait at most the specified `timeout` in seconds until the resource
            is released if the specified timeout is positive, otherwise wait
            indefinitely.
        """
        raise NotImplementedError()

    @property
    def resources(self):
        # type: () -> Iterable[(str)]
        """
        Retrieve all currently registered resource names.

        Returns
        -------
        Iterable[(str)]
            A collection of the registered resource names.
        """
        raise NotImplementedError()

    def has_resource(self, name):
        # type: (str) -> bool
        """
        Check if a resource with the given `name` is registered in the
        ResourceManager.

        Parameters
        ----------
        name : str
            The name of the resource.

        Returns
        -------
        bool
            Whether a resource with the given `name` is registered or not.
        """
        return name in self.resources


class Lock(object):
    """Lock
    Example usage:

    .. code-block:: python

        lock = resource_manager.get_lock("resource-identifier")
        with lock:  # blocks waiting for lock acquisition
            # do something with the lock

    Note: This lock is not *re-entrant*. Repeated calls after already
    acquired will block.
    This is an exclusive lock. For a read/write lock, see :class:`WriteLock`
    and :class:`ReadLock`.
    """

    def acquire(self, blocking=True, timeout=None):
        # type: (bool, float) -> bool
        """
        Acquire the lock. By defaults blocks and waits forever.

        Parameters
        ----------
        blocking : bool
            Block until lock is obtained or return immediately
        timeout : float or None
            Wait at most the specified `timeout` in seconds to acquire the lock
            if the specified timeout is positive, otherwise wait indefinitely.

        Returns
        -------
        bool
            Signal if the lock was acquired

        Raises
        ------
            :class:`LockTimeoutError` if the lock wasn't acquired within `timeout` seconds.
        """
        raise NotImplementedError()

    @property
    def locked(self):
        # type: () -> bool
        """
        Check if the lock is held by someone.

        Returns
        -------
        bool
            Signal if the lock is held by someone.
        """
        raise NotImplementedError()

    def release(self):
        # type: () -> None
        """
        Release the lock.
        """
        raise NotImplementedError()

    @property
    def interrupted(self):
        # type: () -> bool
        """
        Signals that the lock should be released by the current owner.

        Returns
        -------
        bool
            Whether the lock should be released by the current owner.

        """
        raise NotImplementedError()

    def __enter__(self):
        return self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class WriteLock(Lock):
    """Write Lock
    Example usage:

    .. code-block:: python

        lock = resource_manager.get_write_lock("resource-identifier")
        with lock:  # blocks waiting for lock acquisition
            # do something with the lock

    The write lock can not be acquired if the resource is held by any readers
    or writers.
    Note: This lock is not *re-entrant*. Repeated calls after already
    acquired will block.
    This is the write-side of a shared lock.  See :class:`Lock` for a
    standard exclusive lock and :class:`ReadLock` for the read-side of a
    shared lock.
    """
    pass


class ReadLock(Lock):
    """Read Lock
    Example usage:

    .. code-block:: python

        lock = resource_manager.get_read_lock("resource-identifier")
        with lock:  # blocks waiting for outstanding writers
            # do something with the lock

    The read lock blocks if the resource is held by any writers, but multiple
    readers may hold the lock.
    Note: This lock is not *re-entrant*. Repeated calls after already
    acquired will block.
    This is the read-side of a shared lock.  See :class:`Lock` for a
    standard exclusive lock and :class:`WriteLock` for the write-side of a
    shared lock.
    """
    pass


@contextmanager
def acquire(lock, blocking=True, timeout=-1):
    """A context manager to enable usage of `timeout` and `blocking` arguments
     in `with` blocks.

    Example usage:

    .. code-block:: python

        lock = resource_manager.get_write_lock("resource-identifier")
        with acquire(lock, blocking=True, timeout=10):  # blocks waiting for lock acquisition with timeout
            # do something with the lock

    """
    try:
        result = lock.acquire(blocking=blocking, timeout=timeout)
        yield result
    finally:
        if result:
            lock.release()
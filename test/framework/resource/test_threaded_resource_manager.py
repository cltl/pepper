import threading
import time
import unittest

from pepper.framework.resource.api import Lock, ReadLock, WriteLock
from pepper.framework.resource.threaded import ThreadedResourceManager

TIMEOUT=1


class ResourceManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.resource_manager = ThreadedResourceManager()

    def tearDown(self):
        for name in list(self.resource_manager.resources):
            self.resource_manager.retract_resource(name)

    def test_register_resource(self):
        self.resource_manager.provide_resource("test")
        self.assertTrue(self.resource_manager.has_resource("test"))

    def test_register_multiple(self):
        self.resource_manager.provide_resource("test1")
        self.resource_manager.provide_resource("test2")

        self.assertTrue(self.resource_manager.has_resource("test1"))
        self.assertTrue(self.resource_manager.has_resource("test2"))

    def test_unregister_resource(self):
        self.resource_manager.provide_resource("test")

        self.resource_manager.retract_resource("test")
        self.assertFalse(self.resource_manager.has_resource("test"))

    def test_register_resource_only_once(self):
        with self.assertRaises(ValueError):
            self.resource_manager.provide_resource("test")
            self.resource_manager.provide_resource("test")

    def test_unregister_unknown(self):
        with self.assertRaises(KeyError):
            self.resource_manager.provide_resource("test")
            self.resource_manager.retract_resource("ttest")

    def test_get_lock(self):
        self.resource_manager.provide_resource("test")

        lock = self.resource_manager.get_lock("test")
        self.assertIsInstance(lock, Lock)

    def test_get_read_lock(self):
        self.resource_manager.provide_resource("test")

        lock = self.resource_manager.get_read_lock("test")
        self.assertIsInstance(lock, ReadLock)

    def test_get_write_lock(self):
        self.resource_manager.provide_resource("test")

        lock = self.resource_manager.get_write_lock("test")
        self.assertIsInstance(lock, WriteLock)

    def test_await_lock(self):
        self._await_test(Lock, self.resource_manager.get_lock)

    def test_await_read_lock(self):
        self._await_test(ReadLock, self.resource_manager.get_read_lock)

    def test_await_write_lock(self):
        self._await_test(WriteLock, self.resource_manager.get_write_lock)

    def _await_test(self, expectedType, task):
        lock_actor = LockActor(self.resource_manager, task)
        lock_actor.start()

        lock_actor.entry_latch.wait(TIMEOUT)
        # Make sure we get to acquiring the lock
        time.sleep(0.1)
        self.assertIsNone(lock_actor.lock)

        self.resource_manager.provide_resource("other")
        time.sleep(0.1)
        self.assertIsNone(lock_actor.lock)

        self.resource_manager.provide_resource("test")
        lock_actor.exit_latch.wait(0.1)
        self.assertIsInstance(lock_actor.lock, expectedType)

        lock_actor.join(timeout=1)


class LockActor(threading.Thread):
    def __init__(self, resource_manager, task):
        # type: (ThreadedResourceManager, Callable[(str)]) -> None
        super(LockActor, self).__init__(name="LockActor")
        self.resource_manager = resource_manager
        self.task = task
        self.lock = None
        self.entry_latch = threading.Event()
        self.exit_latch = threading.Event()

    def run(self):
        # type: () -> None
        self.entry_latch.set()
        self.lock = self.task("test")
        self.exit_latch.set()

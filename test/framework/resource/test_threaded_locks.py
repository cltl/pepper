import logging
import random
import sys
import threading
import time
import unittest

from pepper.framework.resource.api import Lock, acquire
from pepper.framework.resource.threaded import ThreadedResourceManager


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
logger.setLevel(logging.DEBUG)


TIMEOUT=1


seed = random.randrange(sys.maxsize)
rng = random.Random(seed)
print("Random seed for test:", seed)


class TestActor(threading.Thread):
    def __init__(self, lock, name, termination_condition, critical_task=None):
        # type: (Lock, str, TerminationCondition, Callable[(str)]) -> None
        super(TestActor, self).__init__(name=name)
        self.in_critical = False
        self._termination_cond = termination_condition
        self._critical_task = critical_task
        self._running = True

        self._lock = lock
        self._entered_critical_latch = threading.Event()
        self._left_critical_latch = threading.Event()
        self._entry_latch = threading.Event()
        self._exit_latch = threading.Event()

    def stop(self):
        self._termination_cond.terminate = True
        self._running = False
        self._left_critical_latch.set()
        self._entered_critical_latch.set()
        self._entry_latch.set()
        self._exit_latch.set()

    @property
    def interrupted(self):
        return self._lock.interrupted

    def enter_critical(self):
        self._entered_critical_latch = threading.Event()
        self._entry_latch.set()

        return self._entered_critical_latch

    def exit_critical(self):
        self._left_critical_latch = threading.Event()
        self._exit_latch.set()

        return self._left_critical_latch

    def run(self):
        try:
            self._do_run()
        except AssertionError:
            logger.debug("Test actor interrupted")
        except:
            logger.exception("Test actor failed")
        finally:
            self.stop()

    def _do_run(self):
        while self._running:
            logger.debug(self.name + ": Await entry latch")
            if not self._entry_latch.wait(timeout=TIMEOUT):
                raise AssertionError("Timeout on entry latch")

            self._assert_running()

            logger.debug(self.name + ": Await lock")
            with acquire(self._lock, TIMEOUT):
                logger.debug(self.name + ": In critical")
                self._assert_running()

                self.in_critical = True
                self._entered_critical_latch.set()

                if self._critical_task is not None:
                    logger.debug(self.name + ": Execute critical task")
                    self._critical_task(self.name)

                logger.debug(self.name + ": Await exit latch")
                if not self._exit_latch.wait(timeout=TIMEOUT):
                    raise AssertionError("Timeout on exit latch")

            logger.debug(self.name + ": Exit critical")
            self.in_critical = False
            self._entry_latch.clear()
            self._exit_latch.clear()
            self._left_critical_latch.set()

        logger.debug(self.name + ": Stopped")

    def _assert_running(self):
        if not self._running or self._termination_cond.terminate:
            raise AssertionError(self.name + ": Stopped")


class TerminationCondition(object):
    def __init__(self):
        self._lock = threading.Lock()
        self._terminated = False

    @property
    def terminate(self):
        with self._lock:
            return self._terminated

    @terminate.setter
    def terminate(self, value):
        with self._lock:
            logger.debug("Termination flag set")
            self._terminated = value


class TestBase(unittest.TestCase):
    def assert_in_critical(self, expected, *agents):
        self.assertEqual(len(expected), len(agents))
        self.assertTrue(all(exp == agent.in_critical for exp, agent in zip(expected, agents)),
                        "expected: {0}, was {1}".format(expected, ([agent.in_critical for agent in agents])))

    def exec_with_latch(self, action):
        latch = action()
        logger.debug("Await latch for " + action.__name__)
        latch.wait(timeout=TIMEOUT)


class LockTestCase(TestBase):
    def setUp(self):
        self.termination_condition = TerminationCondition()
        self.actors = []
        self.resource_manager = ThreadedResourceManager()
        self.resource_manager.provide_resource("test")

    def tearDown(self):
        [thread.stop() for thread in self.actors]
        [thread.join() for thread in self.actors]
        self.resource_manager.retract_resource("test")

    def test_exclusive_access(self):
        self.actors = [TestActor(self.resource_manager.get_lock("test"), "actor_1", self.termination_condition),
                       TestActor(self.resource_manager.get_lock("test"), "actor_2", self.termination_condition)]
        [actor.start() for actor in self.actors]

        actor_1, actor_2 = self.actors
        self.assert_in_critical([False, False], actor_1, actor_2)

        self.exec_with_latch(actor_1.enter_critical)
        self.assert_in_critical([True, False], actor_1, actor_2)

        latch = actor_2.enter_critical()
        time.sleep(0.1)
        self.assert_in_critical([True, False], actor_1, actor_2)

        self.exec_with_latch(actor_1.exit_critical)
        latch.wait(TIMEOUT)
        self.assert_in_critical([False, True], actor_1, actor_2)

        self.exec_with_latch(actor_2.exit_critical)
        self.assert_in_critical([False, False], actor_1, actor_2)

    def test_interrupted(self):
        self.actors = [TestActor(self.resource_manager.get_lock("test"), "actor_1", self.termination_condition),
                       TestActor(self.resource_manager.get_lock("test"), "actor_2", self.termination_condition)]
        [actor.start() for actor in self.actors]

        actor_1, actor_2 = self.actors
        self.assert_in_critical([False, False], actor_1, actor_2)

        self.exec_with_latch(actor_1.enter_critical)
        self.assert_in_critical([True, False], actor_1, actor_2)
        self.assertEqual([False, False], [actor_1.interrupted, actor_2.interrupted])

        latch = actor_2.enter_critical()
        time.sleep(0.1)
        self.assert_in_critical([True, False], actor_1, actor_2)
        self.assertEqual([True, True], [actor_1.interrupted, actor_2.interrupted])

        self.exec_with_latch(actor_1.exit_critical)
        latch.wait(TIMEOUT)
        self.assert_in_critical([False, True], actor_1, actor_2)
        self.assertEqual([False, False], [actor_1.interrupted, actor_2.interrupted])

        self.exec_with_latch(actor_2.exit_critical)
        self.assert_in_critical([False, False], actor_1, actor_2)
        self.assertEqual([False, False], [actor_1.interrupted, actor_2.interrupted])


class RWLockTestCase(TestBase):
    def setUp(self):
        self.termination_condition = TerminationCondition()
        self.actors = []
        self.resource_manager = ThreadedResourceManager()
        self.resource_manager.provide_resource("test")

    def tearDown(self):
        [thread.stop() for thread in self.actors]
        [thread.join() for thread in self.actors]
        self.resource_manager.retract_resource("test")

    def test_readers_nonexclusive_access(self):
        self.actors = [TestActor(self.resource_manager.get_read_lock("test"), "reader_1", self.termination_condition),
                       TestActor(self.resource_manager.get_read_lock("test"), "reader_2", self.termination_condition)]
        [actor.start() for actor in self.actors]

        reader_1, reader_2 = self.actors
        self.assert_in_critical([False, False], reader_1, reader_2)

        self.exec_with_latch(reader_1.enter_critical)
        self.assert_in_critical([True, False], reader_1, reader_2)

        self.exec_with_latch(reader_2.enter_critical)
        self.assert_in_critical([True, True], reader_1, reader_2)

        self.exec_with_latch(reader_1.exit_critical)
        self.assert_in_critical([False, True], reader_1, reader_2)

        self.exec_with_latch(reader_2.exit_critical)
        self.assert_in_critical([False, False], reader_1, reader_2)

    def test_writers_exclusive_access(self):
        self.actors = [TestActor(self.resource_manager.get_write_lock("test"), "writer_1", self.termination_condition),
                       TestActor(self.resource_manager.get_write_lock("test"), "writer_2", self.termination_condition),
                       TestActor(self.resource_manager.get_read_lock("test"), "reader_1", self.termination_condition)]
        [actor.start() for actor in self.actors]

        writer_1, writer_2, reader_1 = self.actors
        self.assert_in_critical([False, False, False], writer_1, writer_2, reader_1)

        self.exec_with_latch(writer_1.enter_critical)
        self.assert_in_critical([True, False, False], writer_1, writer_2, reader_1)

        writer_latch = writer_2.enter_critical()
        writer_latch.wait(timeout=0.1)
        self.assert_in_critical([True, False, False], writer_1, writer_2, reader_1)

        reader_latch = reader_1.enter_critical()
        reader_latch.wait(timeout=0.1)
        self.assert_in_critical([True, False, False], writer_1, writer_2, reader_1)

        self.exec_with_latch(writer_1.exit_critical)
        writer_latch.wait(timeout=1)
        self.assert_in_critical([False, True, False], writer_1, writer_2, reader_1)

        self.exec_with_latch(writer_2.exit_critical)
        reader_latch.wait(timeout=1)
        self.assert_in_critical([False, False, True], writer_1, writer_2, reader_1)

        self.exec_with_latch(reader_1.exit_critical)
        self.assert_in_critical([False, False, False], writer_1, writer_2, reader_1)

    def test_writer_priority(self):
        task_invocations = []

        initial_writer = TestActor(self.resource_manager.get_write_lock("test"), "writer_0", self.termination_condition)
        writers = [TestActor(self.resource_manager.get_write_lock("test"), "writer_" + str(i+1), self.termination_condition, task_invocations.append)
                   for i in range(random.randint(2, 9))]
        readers = [TestActor(self.resource_manager.get_read_lock("test"), "reader_" + str(i+1), self.termination_condition, task_invocations.append)
                   for i in range(random.randint(2, 9))]

        self.actors = readers + writers
        random.shuffle(self.actors)
        self.actors = [initial_writer] + self.actors

        [actor.start() for actor in self.actors]

        self.assert_in_critical([False for _ in range(len(self.actors))], *self.actors)

        self.exec_with_latch(initial_writer.enter_critical)
        self.assert_in_critical([True] + [False for _ in range(len(self.actors[1:]))], *self.actors)

        [actor.enter_critical() for actor in self.actors[1:]]
        # We don't reach the latches yet
        time.sleep(0.1)

        self.assert_in_critical([True] + [False for _ in range(len(self.actors[1:]))], *self.actors)

        self.exec_with_latch(initial_writer.exit_critical)
        latches = [actor.exit_critical() for actor in self.actors[1:]]
        for latch in latches:
            latch.wait()

        self.assert_in_critical([False for _ in range(len(self.actors))], *self.actors)

        expected_invocations = ["writer"] * len(writers) + ["reader"] * len(readers)
        self.assertEqual(expected_invocations, [name[:-2] for name in task_invocations])

    def test_is_interrupted(self):
        self.actors = [TestActor(self.resource_manager.get_write_lock("test"), "writer_1", self.termination_condition),
                       TestActor(self.resource_manager.get_write_lock("test"), "writer_2", self.termination_condition),
                       TestActor(self.resource_manager.get_read_lock("test"), "reader_1", self.termination_condition)]
        [actor.start() for actor in self.actors]

        writer_1, writer_2, reader_1 = self.actors
        self.assert_in_critical([False, False, False], writer_1, writer_2, reader_1)

        self.exec_with_latch(writer_1.enter_critical)
        self.assert_in_critical([True, False, False], writer_1, writer_2, reader_1)

        writer_latch = writer_2.enter_critical()
        time.sleep(0.1)
        self.assert_in_critical([True, False, False], writer_1, writer_2, reader_1)
        self.assertEqual([False, False, False], [writer_1.interrupted, writer_2.interrupted, reader_1.interrupted])

        self.exec_with_latch(writer_1.exit_critical)
        writer_latch.wait(timeout=1)
        self.assert_in_critical([False, True, False], writer_1, writer_2, reader_1)

        reader_latch = reader_1.enter_critical()
        time.sleep(0.1)
        self.assert_in_critical([False, True, False], writer_1, writer_2, reader_1)
        self.assertEqual([False, True, False], [writer_1.interrupted, writer_2.interrupted, reader_1.interrupted])

        self.exec_with_latch(writer_2.exit_critical)
        reader_latch.wait()
        self.assert_in_critical([False, False, True], writer_1, writer_2, reader_1)

        writer_latch = writer_1.enter_critical()
        time.sleep(0.1)
        self.assert_in_critical([False, False, True], writer_1, writer_2, reader_1)
        self.assertEqual([False, False, True], [writer_1.interrupted, writer_2.interrupted, reader_1.interrupted])

        self.exec_with_latch(reader_1.exit_critical)
        writer_latch.wait()
        self.assert_in_critical([True, False, False], writer_1, writer_2, reader_1)

        self.exec_with_latch(writer_1.exit_critical)
        self.assert_in_critical([False, False, False], writer_1, writer_2, reader_1)


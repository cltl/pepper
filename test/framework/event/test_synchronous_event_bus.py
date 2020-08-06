import unittest

from pepper.framework.event.api import Event, EventMetadata
from pepper.framework.event.memory import SynchronousEventBus


class SynchronousEventBusTestCase(unittest.TestCase):
    def setUp(self):
        self.event_bus = SynchronousEventBus()

    def test_publish(self):
        event = Event("test payload", EventMetadata())
        self.event_bus.publish("testTopic", event)

        self.assertEqual([ t for t in self.event_bus.topics ], ["testTopic"])

    def test_subscribe(self):
        actual_events = []
        handler = lambda ev: actual_events.append(ev)

        event = Event("test payload", EventMetadata())

        self.event_bus.subscribe("testTopic", handler)
        self.event_bus.publish("testTopic", event)

        self.assertEqual(len(actual_events), 1)
        self.assertEqual(actual_events[0], event)

    def test_multiple_subscribers(self):
        actual_events = []
        handler_one = lambda ev: actual_events.append(ev)
        handler_two = lambda ev: actual_events.append(ev)

        event = Event("test payload", EventMetadata())

        self.event_bus.subscribe("testTopic", handler_one)
        self.event_bus.subscribe("testTopic", handler_two)
        self.event_bus.publish("testTopic", event)

        self.assertEqual(len(actual_events), 2)
        self.assertEqual(actual_events[0], event)
        self.assertEqual(actual_events[1], event)

    def test_multiple_topics(self):
        actual_events = []
        handler_one = lambda ev: actual_events.append(ev)
        handler_two = lambda ev: actual_events.append(ev)

        event_one = Event("test payload one", EventMetadata())
        event_two = Event("test payload two", EventMetadata())

        self.event_bus.subscribe("testTopicOne", handler_one)
        self.event_bus.subscribe("testTopicTwo", handler_two)
        self.event_bus.publish("testTopicOne", event_one)
        self.event_bus.publish("testTopicTwo", event_two)

        self.assertEqual(sorted(t for t in self.event_bus.topics), ["testTopicOne", "testTopicTwo"])
        self.assertEqual(len(actual_events), 2)
        self.assertEqual(actual_events[0], event_one)
        self.assertEqual(actual_events[1], event_two)

    def test_unsubscribe(self):
        actual_events = []
        handler = lambda ev: actual_events.append(ev)

        event = Event("test payload", EventMetadata())

        self.event_bus.subscribe("testTopic", handler)
        self.event_bus.publish("testTopic", event)
        self.event_bus.unsubscribe("testTopic", handler)
        self.event_bus.publish("testTopic", event)

        self.assertEqual(len(actual_events), 1)
        self.assertEqual(actual_events[0], event)


if __name__ == '__main__':
    unittest.main()

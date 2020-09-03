from pepper.framework.di_container import DIContainer


class EventBusContainer(DIContainer):
    @property
    def event_bus(self):
        raise ValueError("No EventBus configured")


class EventBus(object):
    """
    Supports publishing of and subscribing to events based on topics.

    Events published to a topic are delivered to all subscribers in the order
    of their arrival. Publishing and invocation of the subscribed handler
    can be asynchronous. Subscribers receive only events that arrive after they
    subscribed to a topic.
    """

    def publish(self, topic, event):
        raise NotImplementedError()

    def subscribe(self, topic, handler):
        raise NotImplementedError()

    def unsubscribe(self, topic, handler=None):
        raise NotImplementedError()

    @property
    def topics(self):
        raise NotImplementedError()

    @property
    def has_topic(self, topic):
        return topic in self.topics


class Event(object):
    def __init__(self, payload, metadata):
        self._payload = payload
        self._metadata = metadata

    @property
    def metadata(self):
        return self._metadata

    @property
    def payload(self):
        return self._payload


class EventMetadata(object):
    def __init__(self, timestamp=None, offset=None):
        self._timestamp = timestamp
        self._offset = offset

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def offset(self):
        return self._offset
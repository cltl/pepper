class EventBus(object):

    def publish(self, topic, event):
        raise NotImplementedError()

    def subscribe(self, topic, handler):
        raise NotImplementedError()

    @property
    def topics(self):
        raise NotImplementedError()

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
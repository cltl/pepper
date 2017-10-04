from pepper.event import Event


class GestureDetectedEvent(Event):
    def __init__(self, session, callback):
        """
        Word Detected Event.

        Parameters
        ----------
        session: qi.Session
            Session to attach this event to
        callback: callable
            Function to call when event occurs
        """

        super(GestureDetectedEvent, self).__init__(session, callback)

        # Connect to 'ALTactileGesture/Gesture' event
        self._subscriber = self.memory.subscriber("ALTactileGesture/Gesture")
        self._subscriber.signal.connect(self.on_gesture)

        # Subscribe to ALTactileGesture service. This way the events will actually be cast.
        self._detection = self.session.service("ALTactileGesture")
        self._detection.subscribe(self.name)

    def on_gesture(self, gestureName):
        """
        Gesture Detected Event: callback should have identical signature

        Parameters
        ----------
        gestureName: string
            name of gesture detected
        """

        self.callback(gestureName)

    def close(self):
        """Cleanup by unsubscribing from 'ALTactileGesture' service"""
        self._detection.unsubscribe(self.name)


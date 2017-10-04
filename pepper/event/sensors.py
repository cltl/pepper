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

        # Subscribe to ALTactileGesture service. This way the events will actually be cast.
        self._detection = self.session.service("ALTactileGesture")

        self._detection.onGesture.connect(self.on_gesture)

    def on_gesture(self, gesture_name):
        """
        Gesture Detected Event: callback should have identical signature

        Parameters
        ----------
        gesture_name: str
            name of gesture detected
        """

        self.callback(gesture_name)

    def close(self):
        """Cleanup by unsubscribing from 'ALTactileGesture' service"""
        self._detection.unsubscribe(self.name)


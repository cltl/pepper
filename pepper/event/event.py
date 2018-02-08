class Event(object):
    def __init__(self, session, callback):
        """
        Abstract Event, base class for all Concrete Events.

        Parameters
        ----------
        session: qi.Session
            Session to attach this event to
        callback: callable
            Function to call when event occurs
        """
        self._session = session
        self._callback = callback
        self._memory = self.session.service("ALMemory")

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of the Event, which is the name of the (sub)class
        """
        return self.__class__.__name__

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
            Session this event is attached to
        """
        return self._session

    @property
    def callback(self):
        """
        Returns
        -------
        callback: callable
            Function to call on event
        """
        return self._callback

    @property
    def memory(self):
        """
        Returns
        -------
        memory
            Memory Service, containing all events.
        """
        return self._memory

    def close(self):
        """Cleanup: Unsubscribe Event(s)"""
        pass

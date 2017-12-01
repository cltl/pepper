import qi
import time
import logging


class App(object):
    def __init__(self, address):
        """
        Create Pepper Application.

        Parameters
        ----------
        address: (str, int)
            Peppers internet address: (ip, port)

        """
        self.resources = []

        self._address = address
        self._url = "tcp://{}:{}".format(*address)
        self._application = qi.Application([self.name, "--qi-url={}".format(self.url)])
        self._log = logging.getLogger(self.__class__.__name__)

        self.application.start()

    @property
    def log(self):
        """
        Get Logger for application

        Returns
        -------
        log: logging.Logger
        """
        return self._log

    @property
    def address(self):
        """
        Returns
        -------
        address : (str, int)
            Peppers internet address: (ip, port)
        """
        return self._address

    @property
    def url(self):
        """
        Returns
        -------
        url : str
            Peppers internet address: 'tcp://{ip}:{port}'
        """
        return self._url

    @property
    def name(self):
        """
        Returns
        -------
        name: str
            Name of Application, which is the name of the App (sub)class
        """
        return self.__class__.__name__

    @property
    def application(self):
        """
        Returns
        -------
        application: qi.Application
            Application object of the qi framework
        """
        return self._application

    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
            Default Session of the qi Application
        """
        return self.application.session

    def start(self):
        """Start Application (Creating a Session)"""

        self.application.start()

    def run(self):
        """Run Application, Stopping on KeyboardInterrupt"""

        try:
            while True: time.sleep(1)
        except KeyboardInterrupt:
            print("KeyboardInterrupt, Closing Down!")
            self.stop()

    def stop(self):
        """Close Events and Stop Application"""
        for resource in self.resources:
            resource.close()
        self.application.stop()

    def __enter__(self):
        """Start Application when entering the 'with' statement."""
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop Application when exiting the 'with' statement"""
        self.stop()
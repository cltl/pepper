from threading import Thread, Lock
from Queue import Empty
from time import sleep


class Scheduler(Thread):
    """Runs Task Continuously with certain interval"""

    def __init__(self, target, interval=1E-3, name=None, args=(), kwargs={}):
        Thread.__init__(self, name=name)
        self._target = target
        self._interval = interval
        self._args = args
        self._kwargs = kwargs
        self._running = False

        self.daemon = True

    def run(self):
        self._running = True
        while self._running:
            self._target(*self._args, **self._kwargs)
            sleep(self._interval)

    def join(self, timeout=None):
        self._running = False
        Thread.join(self, timeout)


class Mailbox(object):

    EPSILSON = 1E-3

    def __init__(self):
        """Create Mailbox Object"""

        self._mutex = Lock()
        self._mail = None

    def put(self, mail):
        """
        Put new Mail in Mailbox

        Parameters
        ----------
        mail: Any
        """
        self._mail = mail

    def get(self, block=True):
        """
        Get Mail from Mailbox

        Parameters
        ----------
        block: bool
            If True: Wait for Mail until it arrives in Mailbox
            If False: Return Empty Exception when Mailbox is Empty

        Returns
        -------
        mail: Any
        """
        with self._mutex:
            if block:
                while self._mail is None:
                    sleep(Mailbox.EPSILSON)
                return self._get()

            else:
                if self._mail is None:
                    raise Empty
                return self._get()

    def _get(self):
        """
        Get Mail & Empty Mailbox

        Returns
        -------
        mail: Any
        """
        mail = self._mail
        self._mail = None
        return mail
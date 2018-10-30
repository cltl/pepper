from threading import Lock
from Queue import Empty


class Mailbox(object):
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
                    pass
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
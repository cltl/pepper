import logging


class ShortTermMemory(object):
    def __init__(self):
        """
        Access beliefs about this interaction, but forget after turn off
        """
        self.uniqueObjects = set()
        self.allObjects = list()

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    def object_seen(self, object):
        """
        Add object to set and list of objects seen
        """
        self.uniqueObjects.add(object)
        self.allObjects.append(object)



from pepper.framework.abstract.component import AbstractComponent
from pepper.brain import LongTermMemory

from pepper import logger


class BrainComponent(AbstractComponent):
    """
    Exposes the Brain (LongTermMemory) to Applications
    """

    def __init__(self):
        # type: () -> None
        super(BrainComponent, self).__init__()

        self._log.info("Initializing BrainComponent")
        self._brain = LongTermMemory()
        self._log.info("Initialized BrainComponent")

    @property
    def brain(self):
        """
        Brain associated with Application

        Returns
        -------
        brain: LongTermMemory
        """
        return self._brain

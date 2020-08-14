from pepper.framework.abstract import AbstractComponent, AbstractBackend
from pepper.brain import LongTermMemory


class BrainComponent(AbstractComponent):
    """
    Exposes the Brain (LongTermMemory) to Applications
    """

    def __init__(self):
        # type: () -> None
        super(BrainComponent, self).__init__()
        self._brain = LongTermMemory()

    @property
    def brain(self):
        """
        Brain associated with Application

        Returns
        -------
        brain: LongTermMemory
        """
        return self._brain

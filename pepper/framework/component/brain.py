from pepper.framework.abstract import AbstractComponent, AbstractBackend
from pepper.brain import LongTermMemory


class BrainComponent(AbstractComponent):
    """
    Exposes the Brain (LongTermMemory) to Applications

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """

    def __init__(self, backend):
        # type: (AbstractBackend) -> None
        super(BrainComponent, self).__init__(backend)
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

from pepper.framework.abstract import AbstractComponent
from pepper.brain import LongTermMemory


class BrainComponent(AbstractComponent):
    def __init__(self, backend):
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

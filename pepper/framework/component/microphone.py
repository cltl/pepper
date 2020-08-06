from pepper.framework.abstract import AbstractComponent
import numpy as np


class MicrophoneComponent(AbstractComponent):
    """
    Exposes the on_audio event to Applications

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """

    def __init__(self, backend):
        super(MicrophoneComponent, self).__init__(backend)
        self.backend.microphone.callbacks += [self.on_audio]

    def on_audio(self, audio):
        # type: (np.ndarray) -> None
        """
        On Audio Event. Called every time samples have been picked up by microphone

        Parameters
        ----------
        audio: np.ndarray
            Audio Samples
        """
        pass

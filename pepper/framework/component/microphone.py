from pepper.framework import AbstractComponent
import numpy as np


class MicrophoneComponent(AbstractComponent):
    def __init__(self, backend):
        super(MicrophoneComponent, self).__init__(backend)
        self.backend.microphone.callbacks += [self.on_audio]

    def on_audio(self, audio):
        # type: (np.ndarray) -> None
        """
        On Audio Event. Called every time samples have been picked up by microphone

        Parameters
        ----------
        image: np.ndarray
            Camera Frame
        """
        pass

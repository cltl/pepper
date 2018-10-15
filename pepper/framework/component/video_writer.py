from pepper.framework.abstract import AbstractComponent
from pepper.util.image import ImageWriter


class VideoWriter(AbstractComponent):
    def __init__(self, backend):
        """
        Construct VideoWriter Component

        Parameters
        ----------
        backend: Backend
        """
        super(VideoWriter, self).__init__(backend)

        writer = ImageWriter()
        self.backend.camera.callbacks.append(writer.write)
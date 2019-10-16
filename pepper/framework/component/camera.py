from pepper.framework import AbstractComponent, AbstractImage, AbstractBackend


class CameraComponent(AbstractComponent):
    """
    Exposes the on_image event to Applications

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """
    def __init__(self, backend):
        # type: (AbstractBackend) -> None
        super(CameraComponent, self).__init__(backend)
        self.backend.camera.callbacks += [self.on_image]

    def on_image(self, image):
        # type: (AbstractImage) -> None
        """
        On Image Event. Called every time an image was taken by Backend

        Parameters
        ----------
        image: AbstractImage
            Camera Frame
        """
        pass

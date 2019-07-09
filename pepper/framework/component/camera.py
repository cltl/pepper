from pepper.framework import AbstractComponent, AbstractImage


class CameraComponent(AbstractComponent):
    def __init__(self, backend):
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

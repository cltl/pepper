from pepper.framework import AbstractComponent, AbstractImage

from cv2 import resize
import numpy as np

class SceneComponent(AbstractComponent):

    RESOLUTION = 300
    SAMPLES = 10
    DEPTH_THRESHOLD = 0.2

    def __init__(self, backend):
        super(SceneComponent, self).__init__(backend)

        self._theta_map, self._phi_map = np.meshgrid(
            np.linspace(0, np.pi, self.RESOLUTION),
            np.linspace(0, 2 * np.pi, 2 * self.RESOLUTION)
        )
        self._depth_map = np.zeros((2 * self.RESOLUTION, self.RESOLUTION, self.SAMPLES), np.float32)
        self._color_map = np.zeros((2 * self.RESOLUTION, self.RESOLUTION, self.SAMPLES, 3), np.float32)
        self._index_map = np.zeros((2 * self.RESOLUTION, self.RESOLUTION), np.uint8)

        self._last_bounds = None

        self.backend.camera.callbacks += [self.on_image]

    @property
    def depth_map(self):
        return self._depth_map

    @property
    def color_map(self):
        return self._color_map

    @property
    def scatter_map(self):
        indices = self.depth_map[..., -1] > self.DEPTH_THRESHOLD

        if np.mean(indices):
            depth = np.mean(self._depth_map[indices], 1)
            color = np.mean(self._color_map[indices], 1)
            phi = self._phi_map[indices]
            theta = self._theta_map[indices]

            # Spherical to Cartesian Coordinates
            x = depth * np.sin(theta) * np.cos(phi)
            z = depth * np.sin(theta) * np.sin(phi)
            y = depth * np.cos(theta)

            return x - np.mean(x), y + 1.1, z - np.mean(z), color

        return np.array([]), np.array([]), np.array([]), np.array([])

    def on_image(self, image):
        # type: (AbstractImage) -> None
        """
        On Image Event. Called every time an image was taken by Backend

        Parameters
        ----------
        image: AbstractImage
            Camera Frame
        """

        if self._last_bounds and image.bounds.overlap(self._last_bounds) > 0.9:

            color = resize(image.image, image.depth.shape[::-1]).astype(np.float32) / 256
            depth = image.depth.astype(np.float32) / 1000

            phi, theta = np.meshgrid(
                np.linspace((image.bounds.x0+np.pi) * self.RESOLUTION / np.pi,
                            (image.bounds.x1+np.pi) * self.RESOLUTION / np.pi,
                            depth.shape[1]),
                np.linspace((image.bounds.y0+np.pi/2) * self.RESOLUTION / np.pi,
                            (image.bounds.y1+np.pi/2) * self.RESOLUTION / np.pi,
                            depth.shape[0]))

            depth_threshold = image.depth > self.DEPTH_THRESHOLD

            phi = phi[depth_threshold].astype(np.int)
            theta = theta[depth_threshold].astype(np.int)
            depth = depth[depth_threshold]
            color = color[depth_threshold]

            sample_index = self._index_map[phi, theta]

            self._depth_map[phi, theta, sample_index] = depth
            self._color_map[phi, theta, sample_index] = color
            self._index_map[phi, theta] = (self._index_map[phi, theta] + 1) % self.SAMPLES

        self._last_bounds = image.bounds
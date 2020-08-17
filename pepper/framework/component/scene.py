from pepper.framework.abstract import AbstractImage
from pepper.framework.abstract.component import AbstractComponent
from pepper.framework.util import spherical2cartesian

from cv2 import resize
import numpy as np

from typing import Tuple


class SceneComponent(AbstractComponent):
    """
    Construct 3D Scene Based on Camera Data
    """

    RESOLUTION = 200
    SAMPLES = 5
    DEPTH_THRESHOLD = 0.5
    VARIANCE_THRESHOLD = 0.5

    def __init__(self):
        # type: () -> None
        super(SceneComponent, self).__init__()
        self._log.info("Initializing SceneComponent")

        # Create Spherical Coordinate Map
        self._theta_map, self._phi_map = np.meshgrid(
            np.linspace(0, np.pi, self.RESOLUTION, dtype=np.float32),
            np.linspace(0, 2 * np.pi, 2 * self.RESOLUTION, dtype=np.float32))

        # Create Depth, Color and Index Maps
        self._depth_map = np.zeros((2 * self.RESOLUTION, self.RESOLUTION, self.SAMPLES), np.float32)
        self._color_map = np.zeros((2 * self.RESOLUTION, self.RESOLUTION, self.SAMPLES, 3), np.float32)
        self._index_map = np.zeros((2 * self.RESOLUTION, self.RESOLUTION), np.uint8)

        # Previous Camera Bounds (=View), to assess whether camera is stationary
        self._last_bounds = None

        def on_image(image):
            # type: (AbstractImage) -> None
            """
            On Image Event. Called every time an image was taken by Backend

            Parameters
            ----------
            image: AbstractImage
                Camera Frame
            """

            # If Camera is stationary (check to prevent blurry frames to enter data pool)
            if self._last_bounds and image.bounds.overlap(self._last_bounds) > 0.9:

                # Get Color and Depth information from Image
                color = resize(image.image, image.depth.shape[::-1]).astype(np.float32) / 256
                depth = image.depth.astype(np.float32)

                # Get Image Orientation & Spherical Pixel Coordinates
                phi, theta = np.meshgrid(
                    np.linspace(image.bounds.x0 * self.RESOLUTION / np.pi,
                                image.bounds.x1 * self.RESOLUTION / np.pi,
                                depth.shape[1]),
                    np.linspace(image.bounds.y0 * self.RESOLUTION / np.pi,
                                image.bounds.y1 * self.RESOLUTION / np.pi,
                                depth.shape[0]))

                # Discard Pixels that are too close to the camera
                depth_threshold = image.depth > self.DEPTH_THRESHOLD
                phi = phi[depth_threshold]
                theta = theta[depth_threshold]
                depth = depth[depth_threshold]
                color = color[depth_threshold]

                # Convert phi, theta to integer indices
                phi, theta = phi.astype(np.int), theta.astype(np.int)

                # Add Current Sample to Depth/Color Maps
                sample_index = self._index_map[phi, theta]
                self._depth_map[phi, theta, sample_index] = depth
                self._color_map[phi, theta, sample_index] = color

                # Update Index Map
                self._index_map[phi, theta] = (self._index_map[phi, theta] + 1) % self.SAMPLES

            # Update Last Camera Bounds
            self._last_bounds = image.bounds

        # Subscribe to On Image Event
        self.backend.camera.callbacks += [on_image]

    @property
    def scatter_map(self):
        # type: () -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
        """
        Create 3D Scatter Map of Scene

        Returns
        -------
        x, y, z, color: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]
            Numpy Arrays of X, Y, Z and Color Data
        """

        # Get Per Pixel Min and Max Depth
        min_depth = np.min(self._depth_map, -1)
        max_depth = np.max(self._depth_map, -1)

        # Only draw pixels further than DEPTH_THRESHOLD, with less variance as VARIANCE_THRESHOLD
        valid = np.logical_and(min_depth > self.DEPTH_THRESHOLD, max_depth - min_depth < self.VARIANCE_THRESHOLD)

        if np.mean(valid):  # If there is something to draw...

            # Get valid pixels to draw (and average depth and color samples)
            depth = np.mean(self._depth_map[valid], 1)
            color = np.mean(self._color_map[valid], 1)
            phi = self._phi_map[valid]
            theta = self._theta_map[valid]

            # Convert Spherical Coordinates to Cartesian Coordinates
            x, y, z = spherical2cartesian(phi, theta, depth)

            # Return Cartesian Coordinates and Color
            return x, y, z, color

        # Return Empty Result
        return np.array([]), np.array([]), np.array([]), np.array([])

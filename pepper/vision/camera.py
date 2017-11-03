from PIL.ImageEnhance import Contrast, Sharpness
from PIL import Image
from enum import IntEnum


class Resolution(IntEnum):
    """Resolution of Pepper Camera"""

    QQQQVGA = 8     # (40, 30)
    QQQVGA = 7      # (80, 60)
    QQVGA = 0       # (160, 120)
    QVGA = 1        # (320, 240)
    VGA = 2         # (640, 480)
    VGA4 = 3        # (1280, 960)


class ColorSpace(IntEnum):
    """Color Space of Pepper Camera"""

    Yuv = 0
    yUv = 1
    yuV = 2

    Rgb = 3
    rGb = 4
    rgB = 5

    Hsy = 6
    hSy = 7
    hsY = 8

    YUV422 = 9
    YUV = 10
    RGB = 11
    HSY = 12
    BGR = 13

    YYCbCr = 14
    H2RGB = 15
    HSMixed = 16


class Camera:
    """Abstract Base Class for Camera Objects"""

    def get(self):
        """
        Returns
        -------
        vision: PIL.Image.Image
            Image captured by camera object
        """
        raise NotImplementedError()


class SystemCamera(Camera):

    WARM_UP = 30

    def __init__(self, camera = 0):
        """
        Capture images using the webcam of this device

        Parameters
        ----------
        camera
        """

        # Importing cv2 (OpenCV)
        # This way it's not necessary to have the OpenCV library, unless you want to use the webcam.
        import cv2

        self._capture = cv2.VideoCapture(camera)
        self._capture.set(3, 1280)
        self._capture.set(4, 1024)
        for i in range(self.WARM_UP): self._capture.read()

    def get(self):
        import cv2
        status, image = self._capture.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image = Image.fromarray(image)

        image = Contrast(image).enhance(2)
        image = Sharpness(image).enhance(2)

        return image

    def __del__(self):
        self._capture.release()


class PepperCamera(Camera):

    def __init__(self, session, camera_id, resolution = Resolution.VGA, colorspace = ColorSpace.RGB, rate = 5):
        """
        Capture images using Pepper's Camera

        Parameters
        ----------
        session: qi.Session
            Session to hook the camera onto
        resolution: Resolution
            Resolution of the camera
        colorspace: ColorSpace
            Color Space of the camera
        rate: int
            Rate at which camera captures images, should be in range 1..30
        """

        self._session = session
        self._camera_id = camera_id
        self._resolution = resolution
        self._colorspace = colorspace
        self._rate = rate

        self._service = self.session.service("ALVideoDevice")

        self._client = self.service.subscribeCamera(
            self._camera_id, 0, int(self.resolution), int(self.colorspace), self.rate)


    @property
    def session(self):
        """
        Returns
        -------
        session: qi.Session
            Session camera is hooked into
        """
        return self._session

    @property
    def camera_id(self):
        """
        Returns
        -------
        camera_id: str
            Name of the attached camera service subscription
        """
        return self._camera_id

    @property
    def resolution(self):
        """
        Returns
        -------
        resolution: Resolution
            Resolution of Camera
        """
        return self._resolution

    @property
    def colorspace(self):
        """
        Returns
        -------
        colorspace: ColorSpace
            Color Space of Camera
        """
        return self._colorspace

    @property
    def rate(self):
        """
        Returns
        -------
        rate: int
            Frame rate of
        """
        return self._rate

    @property
    def service(self):
        return self._service

    @property
    def client(self):
        return self._client

    def get(self):
        width, height, layers, color_space, seconds, milliseconds, data, camera_id, \
        angle_left, angle_top, angle_right, angle_bottom = self.service.getImageRemote(self.client)

        return Image.frombytes(self.colorspace.name, (width, height), str(data))

    def close(self):
        self.service.unsubscribe(self.camera_id)


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import qi

    session = qi.Session()
    session.connect("tcp://192.168.1.100:9559")

    camera = PepperCamera(session, "CameraTest")
    image = camera.get()
    camera.close()

    plt.imshow(image)
    plt.show()
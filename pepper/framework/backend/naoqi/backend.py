import qi
from naoqi import ALProxy

from pepper import config, logger, CameraResolution
from pepper.framework.abstract.backend import AbstractBackend
from pepper.framework.abstract.microphone import TOPIC as MIC_TOPIC
from pepper.framework.backend.container import BackendContainer
from pepper.framework.backend.naoqi import NAOqiCamera, NAOqiMicrophone, NAOqiTextToSpeech, \
    NAOqiMotion, NAOqiLed, NAOqiTablet
from pepper.framework.backend.system import SystemCamera, SystemMicrophone, SystemTextToSpeech
from pepper.framework.di_container import singleton
from pepper.framework.event.api import EventBusContainer, EventBus
from pepper.framework.resource.api import ResourceManager


class NAOqiBackendContainer(BackendContainer, EventBusContainer):
    logger.info("Initialized NAOqiBackendContainer")
    @property
    @singleton
    def backend(self):
        return NAOqiBackend(self.event_bus, self.resource_manager)


class NAOqiBackend(AbstractBackend):
    """
    Initialize NAOqi Backend

    Parameters
    ----------
    url: str
        NAOqi Robot URL
    camera_resolution: CameraResolution
        NAOqi Camera Resolution
    camera_rate: int
        NAOqi Camera Rate
    microphone_index: int
        NAOqi Microphone Index
    language: str
        NAOqi Language
    use_system_camera: bool
        Use System Camera instead of NAOqi Camera
    use_system_microphone: bool
        Use System Microphone instead of NAOqi Microphone
    use_system_text_to_speech: bool
        Use System TextToSpeech instead of NAOqi TextToSpeech

    See Also
    --------
    http://doc.aldebaran.com/2-5/index_dev_guide.html
    """
    def __init__(self, event_bus, resource_manager,
                 url=config.NAOQI_URL,
                 camera_resolution=config.CAMERA_RESOLUTION, camera_rate=config.CAMERA_FRAME_RATE,
                 microphone_index=config.NAOQI_MICROPHONE_INDEX, language=config.APPLICATION_LANGUAGE,
                 use_system_camera=config.NAOQI_USE_SYSTEM_CAMERA,
                 use_system_microphone=config.NAOQI_USE_SYSTEM_MICROPHONE,
                 use_system_text_to_speech=config.NAOQI_USE_SYSTEM_TEXT_TO_SPEECH):
        # type: (EventBus, ResourceManager, str, CameraResolution, int, int, str, bool, bool, bool) -> None


        self._url = url

        # Create Session with NAOqi Robot
        self._session = self.create_session(self._url)

        # System Camera Override
        if use_system_camera: camera = SystemCamera(camera_resolution, camera_rate, event_bus)
        else: camera = NAOqiCamera(self.session, camera_resolution, camera_rate, event_bus)

        # System Microphone Override
        if use_system_microphone: microphone = SystemMicrophone(16000, 1, event_bus, resource_manager)
        else: microphone = NAOqiMicrophone(self.session, microphone_index, event_bus, resource_manager)

        # System Text To Speech Override
        if use_system_text_to_speech: text_to_speech = SystemTextToSpeech(language, resource_manager)
        else: text_to_speech = NAOqiTextToSpeech(self.session, language, resource_manager)

        # Set Default Awareness Behaviour
        self._awareness = ALProxy("ALBasicAwareness", config.NAOQI_IP, config.NAOQI_PORT)
        self._awareness.setEngagementMode("SemiEngaged")
        self._awareness.setStimulusDetectionEnabled("People", True)
        self._awareness.setStimulusDetectionEnabled("Movement", True)
        self._awareness.setStimulusDetectionEnabled("Sound", True)
        self._awareness.setEnabled(True)

        super(NAOqiBackend, self).__init__(camera, microphone, text_to_speech,
                                           NAOqiMotion(self.session), NAOqiLed(self.session), NAOqiTablet(self.session))

    @property
    def url(self):
        # type: () -> str
        """
        Pepper/Nao Robot URL

        Returns
        -------
        url: str
        """
        return self._url

    @property
    def session(self):
        # type: () -> qi.Session
        """
        Pepper/Nao Robot Session

        Returns
        -------
        session: qi.Session
        """
        return self._session

    @staticmethod
    def create_session(url):
        # type: (str) -> qi.Session
        """
        Create Qi Session with Pepper/Nao Robot

        Parameters
        ----------
        url: str

        Returns
        -------
        session: qi.Session
        """
        application = qi.Application([NAOqiBackend.__name__, "--qi-url={}".format(url)])
        try: application.start()
        except RuntimeError as e:
            raise RuntimeError("Couldn't connect to robot @ {}\n\tOriginal Error: {}".format(url, e))
        return application.session

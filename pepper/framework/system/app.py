from pepper.framework.abstract import AbstractApp
from pepper.framework.system import *
from pepper import config


class SystemApp(AbstractApp):
    def __init__(self):
        super(SystemApp, self).__init__(
            SystemCamera(config.CAMERA_RESOLUTION, config.CAMERA_FRAME_RATE, [self.on_image]),
            SystemMicrophone(config.MICROPHONE_SAMPLE_RATE, config.MICROPHONE_CHANNELS, [self.on_audio]),
            SystemTextToSpeech())
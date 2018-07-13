from pepper.framework.system import *
from pepper.framework.naoqi import *
from pepper.framework.enumeration import *


APP = SystemApp

class MyApp(APP):
    def __init__(self):
        super(MyApp, self).__init__()
        self.text_to_speech.say("Hello, I Just Booted!")

    def on_audio(self, audio):
        self.log.info("Audio: {}".format(audio.shape))

    def on_image(self, image):
        self.log.info("Image: {}".format(image.shape))


if __name__ == '__main__':
    MyApp().start()
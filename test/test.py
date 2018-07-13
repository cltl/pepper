from pepper.framework.system import *
from pepper.framework.naoqi import *
from pepper.framework.enumeration import *


APP = SystemApp

class MyApp(APP):
    def __init__(self):
        super(MyApp, self).__init__()
        self.text_to_speech.say("Hello, I Just Booted!")

    def on_audio(self, audio):
        pass

    def on_image(self, image):
        pass

    def on_utterance(self, audio):
        self.log.info("Utterance {:3.2f}s".format(len(audio) / float(self.microphone.rate)))


if __name__ == '__main__':
    MyApp().start()
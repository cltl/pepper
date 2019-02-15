from pepper.framework import *
from pepper import config

from random import choice


class ContextApp(AbstractApplication,           # Base Application for given Backend
                 StatisticsComponent,           # Microphone/Camera/Speech Statistics
                 BrainComponent,                # Access to Brain
                 ContextComponent,              # Access to Context
                 ObjectDetectionComponent,      # Access to Object Detection Component
                 FaceDetectionComponent,        # Access to Face Detection Component
                 SpeechRecognitionComponent,    # Access to Speech Recognition
                 TextToSpeechComponent):        # Access to Text to Speech

    def __init__(self, backend):
        super(ContextApp, self).__init__(backend)

        # Access Brain (Make sure GraphDB is running)
        self.log.info(self.brain)

        # Start a Chat with somebody (Just chat with a generic human for now)
        self.start_chat("Human")

        print(self.context.location)

    def on_chat_turn(self, utterance):
        # Called every time a human adds an utterance to the chat
        # Just reply with a random statement for now
        self.say(choice(["Interesting", "Right", "I see", "Ok"]))

        print(self.context.objects, self.context.people)

    def say(self, text, animation=None, block=False):
        # Call Text To Speech for given Text
        super(ContextApp, self).say(text, animation, block)

        # Add whatever Pepper says to Chat as an Utterance
        if self.has_chat:
            self.chat.add_utterance(text, me=True)


if __name__ == '__main__':
    # Run Application using Settings in pepper.config
    ContextApp(config.get_backend()).run()

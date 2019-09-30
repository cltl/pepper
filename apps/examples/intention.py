"""Example Application that shows how to work with different Intentions in one Application"""

from pepper.framework import *
from pepper import config

from time import sleep


class MyApplication(AbstractApplication,            # Main Application, inherits from AbstractApplication
                    StatisticsComponent,            # Show Performance Statistics
                    FaceRecognitionComponent,       # Face Recognition
                    SpeechRecognitionComponent,     # Speech Recognition
                    TextToSpeechComponent):         # Text to Speech

    pass  # That's it for the main application, all logic is implemented in the Intentions


# Idle Intention (not in conversation).
# Inherits from AbstractIntention and MyApplication (specified above)
class IdleIntention(AbstractIntention, MyApplication):

    def on_face(self, faces):
        self.log.info(faces)

    # Since MyApplication inherits from FaceRecognitionComponent, the on_face_known event, becomes available here
    def on_face_known(self, faces):

        # When known face is recognized, switch to TalkIntention (now we're in conversation!)
        TalkIntention(self.application, faces[0].name)


# Talk Intention (in conversation!).
# Inherits from AbstractIntention and MyApplication (specified above)
class TalkIntention(AbstractIntention, MyApplication):

    # Called when Intention is Initialized
    def __init__(self, application, speaker):
        super(TalkIntention, self).__init__(application)

        # Save Speaker, to refer to it later!
        self._speaker = speaker

        # Greet Recognized human by name
        self.say("Hello, {}!".format(self._speaker))

    # Called when Human has uttered some sentence
    def on_transcript(self, hypotheses, audio):

        # If Human ends conversation, switch back to Idle Intention
        for hypothesis in hypotheses:

            self.log.debug(hypothesis)

            if hypothesis.transcript.lower() in ["bye bye", "bye", "goodbye", "see you"]:
                # Respond Goodbye, <speaker>!
                self.say("Goodbye, {}!".format(self._speaker))

                # Sleep 5 seconds (else human would be instantly greeted again)
                sleep(5)

                # Switch Back to Idle Intention
                IdleIntention(self.application)

                return

        else:

            # If Human doesn't end the conversation,
            # act as if you understand what he/she is saying :)
            self.say("How interesting!")


if __name__ == '__main__':

    # Initialize Application
    application = MyApplication(config.get_backend())

    # Initialize (Idle) Intention
    IdleIntention(application)

    # Run Application
    application.run()

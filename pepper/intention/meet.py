from pepper.framework import AbstractIntention
from pepper.framework.system import SystemApp
from pepper.language.names import NameParser
from pepper.knowledge import sentences

from random import choice
from time import sleep
from enum import Enum



class MeetAction(Enum):
    LISTENING_FOR_NAME = 0
    VERIFYING_NAME = 1


class MeetIntention(AbstractIntention):

    MIN_SAMPLES = 25

    def __init__(self, app):
        super(MeetIntention, self).__init__(app)

        self._name_parser = NameParser(list(self.app.faces.keys()))

        self._name = None
        self._face = []

        self._action = MeetAction.LISTENING_FOR_NAME

        self.text_to_speech.say("{} {} {}".format(
            choice(sentences.GREETING),
            choice(sentences.INTRODUCE),
            choice(sentences.ASK_NAME)))

    def on_face(self, bounds, face):
        self._face.append(face)

    def on_transcript(self, transcript, audio):
        if self._action == MeetAction.LISTENING_FOR_NAME:

            # Try to parse name
            self.text_to_speech.say(choice(sentences.THINKING))
            parsed_name = self._name_parser.parse_new(audio)

            # If name was heard, ask person to verify it
            if parsed_name:
                self._name, confidence = parsed_name
                self.text_to_speech.say(choice(sentences.VERIFY_NAME).format(self._name))
                self._action = MeetAction.VERIFYING_NAME

            # If no name was heard, kindly ask person to repeat it
            else:
                self.text_to_speech.say("{} {}".format(
                    choice(sentences.DIDNT_HEAR_NAME),
                    choice(sentences.REPEAT_NAME)))

        # If a name was heard, make sure to verify
        elif self._action == MeetAction.VERIFYING_NAME:
            text, confidence = transcript[0]
            for word in text.split():
                # If affirmation was heard
                if word in sentences.AFFIRMATION:
                    # And enough face samples have been gathered
                    if len(self._face) < self.MIN_SAMPLES:
                        self.text_to_speech.say("{} {}".format(
                            choice(sentences.JUST_MET).format(self._name),
                            choice(sentences.MORE_FACE_SAMPLES)))
                        while len(self._face) < self.MIN_SAMPLES:
                            sleep(1)
                        self.text_to_speech.say(choice(sentences.THANK))

                    # The meeting is official!
                    self.text_to_speech.say("{} {}".format(
                        choice(sentences.HAPPY),
                        choice(sentences.JUST_MET).format(self._name)))
                    return

                # If negation was heard, listen for name again.
                elif word in sentences.NEGATION:

                    # Catch sentences that include both a name and a negation
                    parsed_name = self._name_parser.parse_new(audio)
                    if parsed_name and parsed_name[1] > 0.8:
                        self._name, confidence = parsed_name
                        self.text_to_speech.say("{} {}".format(
                            choice(sentences.UNDERSTAND),
                            choice(sentences.VERIFY_NAME).format(self._name)))

                    # Else ask person to repeat name
                    else:
                        self.text_to_speech.say("{} {}".format(
                            choice(sentences.SORRY),
                            choice(sentences.REPEAT_NAME)))
                        self._action = MeetAction.LISTENING_FOR_NAME
                    return


if __name__ == '__main__':
    app = SystemApp()
    intention = MeetIntention(app)
    app.intention = intention
    app.start()
from __future__ import unicode_literals

from pepper.framework import *
from pepper.responder import *

from pepper.framework.component.subtitles import SubtitlesComponent

from pepper import config

from pepper.knowledge import sentences

import numpy as np

from typing import List, Callable
from random import choice
from time import time
import os


RESPONDERS = [
    BrainResponder(),
    VisionResponder(), PreviousUtteranceResponder(), IdentityResponder(), LocationResponder(), TimeResponder(),
    QnAResponder(),
    GreetingResponder(), GoodbyeResponder(), ThanksResponder(), AffirmationResponder(), NegationResponder(),
    WikipediaResponder(),
    WolframResponder(),
    UnknownResponder(),
]


class ResponderApp(AbstractApplication, StatisticsComponent,

                   SubtitlesComponent,

                   DisplayComponent, SceneComponent,  # TODO: (un)comment to turn Web View On/Off

                   ExploreComponent,
                   ContextComponent, BrainComponent, SpeechRecognitionComponent,
                   ObjectDetectionComponent, FaceRecognitionComponent, TextToSpeechComponent):
    pass


class DefaultIntention(AbstractIntention, ResponderApp):

    IGNORE_TIMEOUT = 60

    def __init__(self, application):
        super(DefaultIntention, self).__init__(application)

        self._ignored_people = {}
        self.response_picker = ResponsePicker(self, RESPONDERS + [MeetIntentionResponder()])

    def on_chat_enter(self, name):
        self._ignored_people = {n: t for n, t in self._ignored_people.items() if time() - t < self.IGNORE_TIMEOUT}

        if name not in self._ignored_people:
            self.context.start_chat(name)
            self.say("{}, {}".format(choice(sentences.GREETING), name))

    def on_chat_exit(self):
        self.say("{}, {}".format(choice(sentences.GOODBYE), self.context.chat.speaker))
        self.context.stop_chat()

    def on_chat_turn(self, utterance):
        super(DefaultIntention, self).on_chat_turn(utterance)

        responder = self.response_picker.respond(utterance)

        if isinstance(responder, MeetIntentionResponder):
            MeetIntention(self.application)

        elif isinstance(responder, GoodbyeResponder):
            self._ignored_people[utterance.chat.speaker] = time()
            self.context.stop_chat()


# TODO: What are you thinking about? -> Well, Bram, I thought....

class BinaryQuestionIntention(AbstractIntention, ResponderApp):

    NEGATION = NegationResponder
    AFFIRMATION = AffirmationResponder

    def __init__(self, application, question, callback, responders):
        # type: (AbstractApplication, List[str], Callable[[bool], None], List[Responder]) -> None
        super(BinaryQuestionIntention, self).__init__(application)

        self.question = question
        self.callback = callback

        # Add Necessary Responders if not already included
        for responder_class in [self.NEGATION, self.AFFIRMATION]:
            if not responder_class in [responder.__class__ for responder in responders]:
                responders.append(responder_class())

        self.response_picker = ResponsePicker(self, responders)

        self.say(choice(question))

    def on_chat_turn(self, utterance):
        responder = self.response_picker.respond(utterance)

        if isinstance(responder, self.AFFIRMATION):
            self.callback(True)
        elif isinstance(responder, self.NEGATION):
            self.callback(False)
        else:
            self.say(choice(self.question))


class MeetIntention(AbstractIntention, ResponderApp):
    CUES = ["my name is", "i am", "no my name is", "no i am"]

    def __init__(self, application):
        super(MeetIntention, self).__init__(application)

        self.response_picker = ResponsePicker(self, RESPONDERS)

        self._asrs = [SynchronousGoogleASR(language) for language in ['nl-NL', 'es-ES']]

        self._last_statement_was_name = False
        self._current_name = None
        self._possible_names = {}
        self._denied_names = set()

        self.context.start_chat("Stranger")

        self.say("{} {}".format(choice(sentences.INTRODUCE), choice(sentences.ASK_NAME)))

    def on_chat_exit(self):
        self.context.stop_chat()
        DefaultIntention(self.application)

    def on_transcript(self, hypotheses, audio):
        self._last_statement_was_name = False

        if self._is_name_statement(hypotheses):

            # Parse Audio using Multiple Languages!
            for asr in self._asrs:
                hypotheses.extend(asr.transcribe(audio))

            for hypothesis in hypotheses:

                self._last_statement_was_name = True

                name = hypothesis.transcript.split()[-1]

                # If not already denied
                if name not in self._denied_names and name[0].isupper():

                    # Update possible names with this name
                    if name not in self._possible_names:
                        self._possible_names[name] = 0.0
                    self._possible_names[name] += hypothesis.confidence

            self._current_name = self._get_current_name()

            # If hypotheses about just mentioned name exist -> Ask Verification
            if self._last_statement_was_name and self._current_name:
                self.say(choice(sentences.VERIFY_NAME).format(self._current_name))

    def on_chat_turn(self, utterance):

        # If not already responded to Name Utterance
        if not self._last_statement_was_name:

            # Respond Normally to Whatever Utterance
            responder = self.response_picker.respond(utterance)

            if self._current_name:  # If currently verifying a name

                # If negated, remove name from name hypotheses (and suggest alternative)
                if isinstance(responder, NegationResponder):
                    self._denied_names.add(self._current_name)
                    self._possible_names.pop(self._current_name)
                    self._current_name = self._get_current_name()

                    # Try to Verify next best hypothesis
                    self.say(choice(sentences.VERIFY_NAME).format(self._current_name))

                # If confirmed, store name and start chat with person
                elif isinstance(responder, AffirmationResponder):
                    self.say(choice(sentences.JUST_MET).format(self._current_name))

                    # Save New Person to Memory
                    self._save()

                    # Start new chat and switch intention
                    self.context.start_chat(self._current_name)
                    DefaultIntention(self.application)

                # Exit on User Goodbye
                elif isinstance(responder, GoodbyeResponder):
                    DefaultIntention(self.application)

                else:  # If some other question was asked, remind human of intention
                    self.say(choice(sentences.VERIFY_NAME).format(self._current_name))

            else:  # If no name hypothesis yet exists
                self.say("But, {}".format(choice(sentences.ASK_NAME)))

    def _get_current_name(self):
        if self._possible_names:
            return [n for n, c in sorted(self._possible_names.items(), key=lambda i: i[1], reverse=True)][0]

    def _is_name_statement(self, hypotheses):
        for hypothesis in hypotheses:
            for cue in self.CUES:
                if cue in hypothesis.transcript.lower():
                    return True
        return False

    def _save(self):
        name, features = self._current_name, np.concatenate(self.face_vectors).reshape(-1, OpenFace.FEATURE_DIM)

        if name != "NEW":  # Prevent Overwrite of NEW.bin
            self.face_classifier.add(name, features)
            features.tofile(os.path.join(config.PEOPLE_NEW_ROOT, "{}.bin".format(name)))


if __name__ == '__main__':

    while True:

        # Boot Application
        application = ResponderApp(config.get_backend())

        # Boot Default Intention
        intention = DefaultIntention(application)

        # Run Application
        application.run()

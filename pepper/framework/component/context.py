from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import *
from pepper.framework.sensor import Context, UtteranceHypothesis
from pepper.language import Utterance

from threading import Lock

from time import time

import numpy as np

from typing import Optional


class ContextComponent(AbstractComponent):
    # TODO: Add Min Area for Entry and Exit
    # TODO: Prevent fast switching of people failing

    MIN_PERSON_AREA_IN = 0.5
    MIN_PERSON_DIFFERENCE_IN = 1.5

    CONVERSATION_TIMEOUT = 5

    def __init__(self, backend):
        super(ContextComponent, self).__init__(backend)

        speech_comp = self.require(ContextComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        object_comp = self.require(ContextComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        face_comp = self.require(ContextComponent, FaceRecognitionComponent)  # type: FaceRecognitionComponent
        self.require(ContextComponent, TextToSpeechComponent)  # type: TextToSpeechComponent

        context_lock = Lock()

        self._context = Context()

        self._people_info = []
        self._face_info = []

        def on_transcript(hypotheses, audio):
            """
            Add Transcript to Chat (if a current Chat exists)

            Parameters
            ----------
            hypotheses: List[UtteranceHypothesis]
            audio: np.ndarray
            """

            with context_lock:
                if self.context.chatting:

                    # Add ASR Transcript to Chat as Utterance
                    self.context.chat.add_utterance(hypotheses, False)

                    # Call On Chat Turn Event
                    self.on_chat_turn(self.context.chat.last_utterance)

        def get_closest_person(people):
            if people:
                if len(people) == 1:
                    if people[0].bounds.area >= self.MIN_PERSON_AREA_IN:
                        return people[0]
                else:

                    # Sort them by proximity
                    people_sorted = np.argsort([person.bounds.area for person in people])[::-1]

                    # Identify the two closest individuals
                    closest = people[people_sorted[0]]
                    next_closest = people[people_sorted[1]]

                    if closest.bounds.area >= self.MIN_PERSON_AREA_IN:
                        if closest.bounds.area >= self.MIN_PERSON_DIFFERENCE_IN * next_closest.bounds.area:
                            return closest

        def get_face(person, faces):
            for face in faces:
                if face.bounds.is_subset_of(person.bounds):
                    return face

        def on_image(image, orientation):

            closest_person = get_closest_person(self._people_info)

            if closest_person:

                closest_face = get_face(closest_person, self._face_info)

                if closest_face and not self.context.chatting:
                    with context_lock:
                        self.on_person_enter(closest_face)

            elif self.context.chatting:
                with context_lock:
                    self.on_person_exit()

            # Wipe Face and People info after use
            self._face_info = []
            self._people_info = []

        def on_object(image, objects):
            self._people_info = [obj for obj in objects if obj.name == "person"]
            self.context.add_objects(objects)

        def on_face(people):
            self._face_info = people
            self.context.add_people(people)

        # Link Transcript, Object and Face Events to Context
        speech_comp.on_transcript_callbacks.insert(0, on_transcript)
        object_comp.on_object_callbacks.insert(0, on_object)
        face_comp.on_face_callbacks.insert(0, on_face)

        # Add On Image Callback
        self.backend.camera.callbacks += [on_image]

    @property
    def context(self):
        # type: () -> Context
        """
        Returns
        -------
        context: Context
            Current Context
        """
        return self._context

    def say(self, text, animation=None, block=False):
        # Call super (TextToSpeechComponent)
        super(ContextComponent, self).say(text, animation, block)

        # Add Utterance to Chat
        if self.context.chatting:
            self.context.chat.add_utterance([UtteranceHypothesis(text, 1)], me=True)

    def on_chat_turn(self, utterance):
        # type: (Utterance) -> None
        """
        On Chat Turn Callback, called every time the speaker utters some Utterance

        Parameters
        ----------
        utterance: Utterance
            Utterance speaker uttered
        """
        pass

    def on_person_enter(self, person):
        pass

    def on_person_exit(self):
        pass

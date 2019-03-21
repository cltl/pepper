from . import SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent, TextToSpeechComponent
from ..sensor import Context, UtteranceHypothesis
from ..abstract import AbstractComponent

from pepper.language import Utterance

from collections import deque
from threading import Thread, Lock
from time import time

from typing import Deque

import numpy as np


class ContextComponent(AbstractComponent):
    # TODO: Prevent fast switching of people failing

    # Minimum Distance of Person to Enter/Exit Conversation
    PERSON_AREA_ENTER = 0.5
    PERSON_AREA_EXIT = 0.2

    # Minimum Distance Difference of Person to Enter/Exit Conversation
    PERSON_DIFF_ENTER = 1.5
    PERSON_DIFF_EXIT = 1.1

    CONVERSATION_TIMEOUT = 5

    def __init__(self, backend):
        super(ContextComponent, self).__init__(backend)

        speech_comp = self.require(ContextComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        object_comp = self.require(ContextComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        face_comp = self.require(ContextComponent, FaceRecognitionComponent)  # type: FaceRecognitionComponent
        self.require(ContextComponent, TextToSpeechComponent)  # type: TextToSpeechComponent

        self._conversation_time = 0

        context_lock = Lock()

        self._context = Context()

        self._face_vectors = deque(maxlen=50)

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
                if self.context.chatting and hypotheses:

                    # Add ASR Transcript to Chat as Utterance
                    self.context.chat.add_utterance(hypotheses, False)

                    # Call On Chat Turn Event
                    self.on_chat_turn(self.context.chat.last_utterance)

        def get_closest_person(people):

            person_area_threshold = (self.PERSON_AREA_EXIT if self.context.chatting else self.PERSON_AREA_ENTER)
            person_diff_threshold = (self.PERSON_DIFF_EXIT if self.context.chatting else self.PERSON_DIFF_ENTER)

            if people:
                if len(people) == 1:
                    if people[0].bounds.area >= person_area_threshold:
                        return people[0]
                else:

                    # Sort them by proximity
                    people_sorted = np.argsort([person.bounds.area for person in people])[::-1]

                    # Identify the two closest individuals
                    closest = people[people_sorted[0]]
                    next_closest = people[people_sorted[1]]

                    if closest.bounds.area >= person_area_threshold:
                        if closest.bounds.area >= person_diff_threshold * next_closest.bounds.area:
                            return closest

        def get_face(person, faces):
            for face in faces:
                if face.bounds.is_subset_of(person.bounds):
                    return face

        def on_image(image, orientation):

            # Determine Conversation Partner
            closest_person = get_closest_person(self._people_info)

            if closest_person:
                closest_face = get_face(closest_person, self._face_info)

                if closest_face:

                    self._conversation_time = time()

                    if self.context.chatting:
                        self._face_vectors.append(closest_face.representation)
                    else:
                        self._face_vectors.clear()
                        Thread(target=self.on_person_enter, args=(closest_face,)).start()

            elif self.context.chatting and time() - self._conversation_time > self.CONVERSATION_TIMEOUT:
                with context_lock:
                    self._face_vectors.clear()
                    self.on_person_exit()

            # Wipe face and people info after use
            self._face_info = []
            self._people_info = []

        def on_object(image, objects):
            self._people_info = [obj for obj in objects if obj.name == "person"]
            self.context.add_objects(objects)

        def on_face(people):
            self._face_info = people
            self.context.add_people(people)

        # Link Transcript, Object and Face Events to Context
        speech_comp.on_transcript_callbacks.append(on_transcript)
        object_comp.on_object_callbacks.append(on_object)
        face_comp.on_face_callbacks.append(on_face)

        # Add On Image Callback
        self.backend.camera.callbacks.append(on_image)

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

    @property
    def face_vectors(self):
        # type: () -> Deque[np.ndarray]
        return self._face_vectors

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

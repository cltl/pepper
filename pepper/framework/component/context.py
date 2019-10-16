from . import SpeechRecognitionComponent, ObjectDetectionComponent, FaceRecognitionComponent, TextToSpeechComponent
from ..context import Context
from ..sensor import UtteranceHypothesis, Object, Face, FaceClassifier
from ..abstract import AbstractComponent, AbstractImage, AbstractBackend

from pepper.language import Utterance
from pepper import config

from collections import deque
from threading import Thread, Lock
from time import time

from typing import Deque, List

import numpy as np


class ContextComponent(AbstractComponent):
    """
    Exposes Context to Applications and contains logic to determine whether conversation should start/end.

    Parameters
    ----------
    backend: AbstractBackend
        Application Backend
    """

    # TODO: Split into two Components? ContextComponent & ConversationComponent?

    # Minimum Distance of Person to Enter/Exit Conversation
    PERSON_AREA_ENTER = 0.25
    PERSON_AREA_EXIT = 0.2

    # Minimum Distance Difference of Person to Enter/Exit Conversation
    PERSON_DIFF_ENTER = 1.5
    PERSON_DIFF_EXIT = 1.1

    # TODO: Should this be a pepper.config variable? YES!
    # Number of seconds of inactivity before conversation times out
    CONVERSATION_TIMEOUT = 30

    def __init__(self, backend):
        # type: (AbstractBackend) -> None
        super(ContextComponent, self).__init__(backend)

        # The ContextComponent requires the following Components:
        speech_comp = self.require(ContextComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        object_comp = self.require(ContextComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        face_comp = self.require(ContextComponent, FaceRecognitionComponent)  # type: FaceRecognitionComponent
        self.require(ContextComponent, TextToSpeechComponent)  # type: TextToSpeechComponent

        # Initialize the Context for this Application
        self._context = Context()

        # To keep track of conversation duration
        self._conversation_time = time()

        # Store the last n faces, to possibly store as a 'known person' later on
        self._face_vectors_max = 50
        self._face_vectors = deque(maxlen=self._face_vectors_max)

        # Needed for the in/out conversation logic, to keep track of peoples bodies/faces as time moves on
        self._people_info = []
        self._face_info = []

        # Make sure to stay synchronized
        context_lock = Lock()

        # << Private (to this component) Functions declared within __init__ >>
        # These functions are declared within the __init__ as to not clutter the Application with declarations.
        # This is an artifact of having applications inherit from all Components:
        #   All of the components public/private variables become available in the application.
        #   The only way to hide variables/functions (and limit clutter) is to define these within __init__
        # One could think of solutions without these artifacts that may be preferred to the chosen method!

        def on_transcript(hypotheses, audio):
            # type: (List[UtteranceHypothesis], np.ndarray) -> None
            """
            Add Transcript to Chat (if a current Chat exists)

            Parameters
            ----------
            hypotheses: List[UtteranceHypothesis]
            audio: np.ndarray
            """

            with context_lock:
                if self.context.chatting and hypotheses:

                    # TODO: Tell user you are thinking about their utterance (useful if thinking takes a long time)
                    # self.say(choice(sentences.THINKING), block=False)

                    # Add ASR Hypotheses to Chat as Utterance
                    utterance = self.context.chat.add_utterance(hypotheses, False)

                    # Call On Chat Turn Event
                    self.on_chat_turn(utterance)

        def get_closest_people(people):
            # type: (List[Face]) -> List[Face]
            """
            Get Person or People closest to Robot (as they may be subject to conversation)

            Parameters
            ----------
            people: List[Face]
                People, as represented by their face (id)

            Returns
            -------
            closest_people: List[Face]
            """

            # To be considered 'closest' people need to make up a predefined area of the camera view
            # This area is defined differently when in conversation then when not in conversation,
            #   this removes the problems one gets when one person is right on the threshold ("hi", "bye", "hi", "bye")
            person_area_threshold = (self.PERSON_AREA_EXIT if self.context.chatting else self.PERSON_AREA_ENTER)
            people_in_range = [person for person in people if person.image_bounds.area >= person_area_threshold]

            # To be considered 'uniquely closest' a person must be closer to the next closest person
            # If this is not the case, and multiple people are close enough, a group conversation will start!
            person_diff_threshold = (self.PERSON_DIFF_EXIT if self.context.chatting else self.PERSON_DIFF_ENTER)

            # If only one person is in range
            if len(people_in_range) == 1:

                # Return that person (as a list of length 1, keeping return values consistent!)
                return [people_in_range[0]]

            # Else If multiple people are in range
            elif len(people_in_range) >= 2:

                # Sort them by proximity
                people_sorted = np.argsort([person.image_bounds.area for person in people_in_range])[::-1]

                # Identify the two closest individuals
                closest = people_in_range[people_sorted[0]]
                next_closest = people_in_range[people_sorted[1]]

                # If the closest individual is significantly (by a predefined fraction) closer than the next one
                if closest.image_bounds.area >= person_diff_threshold * next_closest.image_bounds.area:

                    # Return Closest Individual
                    return [closest]

                # If people are the same distance apart
                else:

                    # Return all People
                    return people_in_range

            # Else (No people are in range)
            else:

                # Return empty list
                return []

        def get_face_of_person(person, faces):
            # type: (Object, List[Face]) -> Face
            """
            Get Face Corresponding with Person

            Persons are identified by Objects (from COCO Object Detection), while Faces are identified by OpenFace.
            This function looks at the bounding boxes of both and returns the face that corresponds with this person.

            Parameters
            ----------
            person: Object
            faces: List[Face]

            Returns
            -------
            face: Face
            """

            for face in faces:
                # TODO: Make sure face bounds are always a subset of 'person' object bounds, else: trouble imminent!
                if face.image_bounds.is_subset_of(person.image_bounds):
                    return face

        def enter_chat(name):
            # Call on Chat Enter Threaded (we are in the 'CameraThread', which we don't want to block)
            Thread(target=self.on_chat_enter, args=(name,)).start()

            # Reset Conversation time to NOW
            self._conversation_time = time()

            # Clear Face Vectors, since a new person (or persons) will be subject to conversation now
            self._face_vectors.clear()

        def exit_chat():
            self.on_chat_exit()
            self._face_vectors.clear()

        def on_image(image):
            # type: (AbstractImage) -> None
            """
            Private On Image Event

            Figure out with who(m) a conversation is held and call on_chat_enter/exit appropriately

            The Image parameter is not directly used, but the timing of the on_image event is perfect for this logic,
                since conversation information can only be updated after a new image has been taken and is processed.

            This function does require the image to be processed using (COCO) Object Detection and Face Recognition,
                as such, these requirements are listed (and enforced) in __init__

            Parameters
            ----------
            image: AbstractImage
            """

            # Get People within Conversation Bounds
            closest_people = get_closest_people(self._people_info)

            # If no current Conversation is happening
            if not self.context.chatting:

                # If one person is closest and his/her face is identifiable -> Start One-on-One Conversation
                if len(closest_people) == 1:
                    closest_person = closest_people[0]
                    closest_face = get_face_of_person(closest_person, self._face_info)

                    if closest_face:
                        enter_chat(closest_face.name)

                # If multiple people are in range, with nobody seemingly closest -> Start Group Conversation
                elif len(closest_people) >= 2:
                    enter_chat(config.HUMAN_CROWD)

            # If a Conversation is currently happening
            elif self.context.chatting:

                # When talking to a Group
                if self.context.chat.speaker == config.HUMAN_CROWD:

                    # If still in conversation with Group, update conversation time (and thus continue conversation)
                    if len(closest_people) >= 2:
                        self._conversation_time = time()

                    # Else, when Group Conversation times out
                    elif time() - self._conversation_time >= self.CONVERSATION_TIMEOUT:

                        # If a single Person enters conversation at this point -> Start conversation with them
                        if len(closest_people) == 1:
                            closest_face = get_face_of_person(closest_people[0], self._face_info)

                            if closest_face:
                                enter_chat(closest_face.name)

                        # Otherwise, Exit Chat with Group
                        else: exit_chat()

                else:  # When talking to a specific Person

                    # If still in conversation with Person, update conversation time (and thus continue conversation)
                    if len(closest_people) == 1:
                        closest_face = get_face_of_person(closest_people[0], self._face_info)

                        if closest_face:

                            # If Still Chatting with Same Person -> Update Conversation Time & Face Vectors
                            # Also continue when person is "NEW", to combat "Hello Stranger" mid conversation...
                            if closest_face.name in [self.context.chat.speaker, FaceClassifier.NEW]:
                                self._conversation_time = time()
                                self._face_vectors.append(closest_face.representation)

                            # If Chatting to Unknown Person (Stranger) and Known Person Appears -> Switch Chat to Known
                            elif self.context.chat.speaker == config.HUMAN_UNKNOWN and \
                                    closest_face.name != config.HUMAN_UNKNOWN:
                                enter_chat(closest_face.name)

                    # Else, when conversation times out with specific Person
                    elif time() - self._conversation_time >= self.CONVERSATION_TIMEOUT:

                        # If another Person enters conversation at this point -> Start Conversation with them
                        if len(closest_people) == 1:
                            closest_face = get_face_of_person(closest_people[0], self._face_info)

                            if closest_face:
                                enter_chat(closest_face.name)

                        # If Group enters conversation at this point -> Start Conversation with them
                        if len(closest_people) >= 2:
                            enter_chat(config.HUMAN_CROWD)

                        # Otherwise, exit chat with specific Person
                        else: exit_chat()

                # Wipe face and people info after use
                self._face_info = []
                self._people_info = []

        def on_object(objects):
            # type: (List[Object]) -> None
            """
            Private On Object Event

            Updates Objects known to Context and filters out people for Conversation Logic

            Parameters
            ----------
            objects: List[Object]
            """
            # Update Context with Perceived Objects
            self.context.add_objects(objects)

            # Add Perceived People to People Info
            self._people_info = [obj for obj in objects if obj.name == "person"]

        def on_face(people):
            # type: (List[Face]) -> None
            """
            Private On Face Event

            Updates People known to Context and adds people to Conversation Logic

            Parameters
            ----------
            people: List[Face]
            """
            # Update Context with Perceived People
            self.context.add_people(people)

            # Add Perceived Faces to Face Info
            self._face_info = people

        # Make sure Private Callback functions are actually called
        speech_comp.on_transcript_callbacks.append(on_transcript)  # Link on_transcript event from SpeechComponent
        object_comp.on_object_callbacks.append(on_object)  # Link on_object event from ObjectDetectionComponent
        face_comp.on_face_callbacks.append(on_face)  # Link on_face event from FaceDetectionComponent
        self.backend.camera.callbacks.append(on_image)  # Link on_image event from Backend Camera

    @property
    def context(self):
        # type: () -> Context
        """
        Reference to Context

        Returns
        -------
        context: Context
            Current Context
        """
        return self._context

    @property
    def face_vectors(self):
        # type: () -> Deque[np.ndarray]
        """
        Returns Face Vectors obtained during one-on-one conversation. These may be used to store a known person

        Returns
        -------
        face_vectors: Deque[np.ndarray]
            Face Representations as numpy.ndarrays
        """
        return self._face_vectors

    def say(self, text, animation=None, block=False):
        # type: (str, str, bool) -> None
        """
        Say Text (with optional Animation) through Text-to-Speech

        This overrides TextToSpeechComponent.say and adds the text to the current chat (if chatting)

        Parameters
        ----------
        text: str
            Text to say through Text-to-Speech
        animation: str or None
            (Naoqi) Animation to play
        block: bool
            Whether this function should block or immediately return after calling
        """

        # Call super TextToSpeechComponent (this is why it is a dependency)
        super(ContextComponent, self).say(text, animation, block)

        # Add Utterance to Chat as Robot Utterance (if chatting)
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

    def on_chat_enter(self, person):
        # type: (str) -> None
        """
        On Chat Enter Event. Called every time the conversation logic decides a conversation should start.

        When called, this does not actually automatically start a conversation, this is up to the user to decide.
        Conversations can be started anytime by calling ContextComponent.context.start_chat().

        Parameters
        ----------
        person: str
            The person (or group of people: config.HUMAN_CROWD), the conversation should start with.
        """
        pass

    def on_chat_exit(self):
        # type: () -> None
        """
        On Chat Exit Event. Called every time the conversation logic decides a conversation should stop.

        When called, this does not actually automatically stop a conversation, this is up to the user to decide.
        Conversations can be stopped anytime by calling ContextComponent.context.stop_chat().
        """
        pass

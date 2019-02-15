from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import SpeechRecognitionComponent, ObjectDetectionComponent, FaceDetectionComponent
from pepper.framework.sensor import Context
from pepper.language import Chat, Utterance, NameParser
from pepper import config

from typing import Optional


class ContextComponent(AbstractComponent):
    def __init__(self, backend):
        super(ContextComponent, self).__init__(backend)

        speech_comp = self.require(ContextComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        object_comp = self.require(ContextComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent
        face_comp = self.require(ContextComponent, FaceDetectionComponent)  # type: FaceDetectionComponent

        name_parser = NameParser(config.PEOPLE_FRIENDS_NAMES)

        self._context = Context()
        self._chat = None

        def on_transcript(hypotheses, audio):
            """
            Add Transcript to Chat (if a current Chat exists)

            Parameters
            ----------
            hypotheses: List[ASRHypothesis]
            audio: np.ndarray
            """
            if self.has_chat:
                self._chat.add_utterance(name_parser.parse_known(hypotheses).transcript, False)
                self.on_chat_turn(self._chat.last_utterance)

        speech_comp.on_transcript_callbacks.insert(0, on_transcript)
        object_comp.on_object_callbacks.insert(0, lambda image, objects: self.context.add_objects(objects))
        face_comp.on_face_known_callbacks.insert(0, self.context.add_people)

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
    def chat(self):
        # type: () -> Optional[Chat]
        """
        Returns
        -------
        chat: Chat
            Current Chat
        """
        return self._chat

    @property
    def has_chat(self):
        # type: () -> bool
        """
        Returns
        -------
        has_chat: bool
            True if a chat is active
        """
        return self._chat is not None

    def start_chat(self, speaker):
        # type: (str) -> None
        """
        Start New Chat

        Parameters
        ----------
        speaker: str
            Speaker to start chat with
        """
        self._chat = Chat(speaker, self._context)
        self._context.add_chat(self._chat)

    def end_chat(self):
        # type: () -> None
        """End Current Chat"""
        self._chat = None

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

from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import SpeechRecognitionComponent
from pepper.framework.sensor import Context
from pepper.language import Chat, Utterance, NameParser
from pepper import config

from typing import Optional


class ContextComponent(AbstractComponent):
    _chat = None  # type: Chat

    def __init__(self, backend):
        super(ContextComponent, self).__init__(backend)

        self._context = Context()
        self._chat = None

        name_parser = NameParser(config.PEOPLE_FRIENDS_NAMES)

        def add_transcript_to_chat(hypotheses, audio):
            if self.has_chat:
                self._chat.add_utterance(name_parser.parse_known(hypotheses).transcript, False)
                self.on_chat_turn(self._chat.last_utterance)

        speech = self.require(ContextComponent, SpeechRecognitionComponent)  # type: SpeechRecognitionComponent
        speech.on_transcript_callbacks.insert(0, add_transcript_to_chat)

    @property
    def context(self):
        # type: () -> Context
        return self._context

    @property
    def chat(self):
        # type: () -> Optional[Chat]
        """
        Returns
        -------
        chat: Chat
        """
        return self._chat

    @property
    def has_chat(self):
        # type: () -> bool
        return self._chat is not None

    def start_chat(self, speaker):
        # type: (str) -> None
        self._chat = Chat(speaker, self._context)
        self._context.last_chat = self._chat

    def end_chat(self):
        # type: () -> None
        self._chat = None

    def on_chat_turn(self, utterance):
        # type: (Utterance) -> None
        pass

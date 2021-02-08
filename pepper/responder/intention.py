from .responder import Responder, ResponderType


class MeetIntentionResponder(Responder):
    CUES = [
        "let's meet",
        "want to meet",
        "my name is",
    ]

    @property
    def type(self):
        return ResponderType.Intention

    @property
    def requirements(self):
        return []

    def respond(self, utterance, app):
        for cue in self.CUES:
            if cue in utterance.transcript.lower():
                return 1, lambda: None

import enum


class UtteranceType(enum.Enum):
    STATEMENT = 0
    QUESTION = 1
    EXPERIENCE = 2


class Time(enum.Enum):
    """
    This will be used in the future to represent tense
    """
    PAST = -1
    PRESENT = 0
    FUTURE = 1


class Emotion(enum.Enum):
    """
    This will be used in the future to represent emotion
    """
    ANGER = 0
    DISGUST = 1
    FEAR = 2
    JOY = 3
    SADNESS = 4
    SURPRISE = 5
    NEUTRAL = 6

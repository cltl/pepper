from .responder import Responder, ResponderType

from pepper.framework import *
from pepper.language import Utterance
from pepper.knowledge import animations, QnA
from pepper import config

from typing import Optional, Union, Tuple, Callable

from random import choice


class VisionResponder(Responder):

    SEE_OBJECT = [
        "what do you see",
        "what can you see",
        "what did you see",
        "what have you seen"
    ]

    SEE_PERSON = [
        "who do you see",
        "who can you see",
    ]

    SEE_PERSON_ALL = [
        "who did you see",
        "who have you seen"
    ]

    SEE_SPECIFIC = [
        "do you see ",
        "can you see ",
        "where is the "
    ]

    I_SEE = [
        "I see",
        "I can see",
        "I think I see",
        "I observe",
    ]

    I_SAW = [
        "I saw",
        "I have seen",
        "I think I observed"
    ]

    NO_OBJECT = [
        "I don't see anything",
        "I don't see any object",
    ]

    NO_PEOPLE = [
        "I don't see anybody I know",
        "I don't see familiar faces",
        "I cannot identify any of my friends",
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [AbstractApplication, TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[AbstractApplication, TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        objects = [obj.name for obj in utterance.chat.context.objects]
        people = [p.name for p in utterance.chat.context.people]

        all_people = [p.name for p in utterance.chat.context.all_people]

        # Enumerate Currently Visible Objects
        if utterance.transcript.lower() in self.SEE_OBJECT:
            if objects:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SEE), self._objects_to_sequence(objects)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_OBJECT))

        # Enumerate Currently Visible People
        elif utterance.transcript.lower() in self.SEE_PERSON:
            if people:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SEE), self._people_to_sentence(people)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_PEOPLE))

        # Enumerate All Observed People
        elif utterance.transcript.lower() in self.SEE_PERSON_ALL:
            if all_people:
                return 1, lambda: app.say("{} {}".format(choice(self.I_SAW), self._people_to_sentence(all_people)))
            else:
                return 0.5, lambda: app.say(choice(self.NO_PEOPLE))

        # Respond to Individual Object Queries
        else:
            for cue in self.SEE_SPECIFIC:
                if cue in utterance.transcript.lower():
                    for obj in utterance.context.objects:
                        if obj.name.lower() in utterance.transcript.lower():
                            return 1.0, lambda: self._point_to_objects(app, obj)

                    return 1.0, lambda: app.say("I cannot see {}".format(self._insert_a_an(utterance.tokens[-1])))

    def _point_to_objects(self, app, obj):
        app.say("I can see {}".format(self._insert_a_an(obj.name)))
        app.motion.point(obj.direction, speed=0.2)
        app.motion.look(obj.direction, speed=0.1)
        app.say("There it is!!")


    @staticmethod
    def _insert_a_an(word):
        if word[0] in "euioa":
            return "an {}".format(word)
        else:
            return "a {}".format(word)

    @staticmethod
    def _objects_to_sequence(objects):
        object_count = {}

        for obj in objects:
            if not obj in object_count:
                object_count[obj] = 0

            object_count[obj] += 1

        items = [(name + ("s" if count > 1 else ""), count) for name, count in object_count.items()]
        if len(items) == 0:
            return "I don't see any objects, yet!"
        if len(items) == 1:
            return "{} {}".format(items[0][1], items[0][0])
        else:
            return "{} and {}.".format(", ".join("{} {}".format(i[1], i[0]) for i in items[:-1]),
                                       "{} {}".format(items[-1][1], items[-1][0]))

    @staticmethod
    def _people_to_sentence(people):
        if len(people) == 1:
            return people[0]
        else:
            return "{} and {}.".format(", ".join(people[:-1]), people[-1])


class PreviousUtteranceResponder(Responder):

    CUE = [
        "what did you say",
        "i didn't hear you",
        "i can't hear you",
        "come again",
        "excuse me",
    ]

    REPEAT = "I said:"

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        for cue in self.CUE:
            if cue in utterance.transcript.lower():
                for u in utterance.chat.utterances[:-1][::-1]:
                    if u.me and not u.transcript.startswith(self.REPEAT):
                        return 1.0, lambda: app.say(text="{} {}".format(self.REPEAT, u.transcript),
                                                    animation=animations.EXPLAIN)
                return 1.0, lambda: app.say("I didn't say anything yet...")


class LocationResponder(Responder):

    CUE_FULL = [
        "where are we",
        "where are you",
        "where we are",
        "where you are",
        "what is here",
    ]

    CUE_SET_LOCATION = [
        "we are in ",
    ]

    CUE_GUESS_LOCATION = [
        "guess where we are",
        "figure out where we are",
        "guess where we are",
    ]

    ANSWER_GUESS = [
        "I think we are in ",
        "It looks a lot like ",
        "I believe this is ",
        "I have been here before. It is ",
    ]

    ANSWER_FAILED_GUESS = [
        "I could not figure out where we are",
        "I am not sure I have been here",
        "This place does not look like anywhere have been before",
        "Maybe many things have changed, but I cannot figure out what this place is",
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent, BrainComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent, BrainComponent]) -> Optional[Tuple[float, Callable]]
        # Respond where we are
        if utterance.transcript.lower() in self.CUE_FULL:
            return 1, lambda: app.say(self._location_to_text(utterance.chat.context.location))

        # Guess where we are
        if utterance.transcript.lower() in self.CUE_GUESS_LOCATION:
            if utterance.context.location.label == utterance.context.location.UNKNOWN:
                guess = app.brain.reason_location(utterance.context)
                if guess:
                    utterance.context.location.label = guess
                    app.brain.set_location_label(guess)
                    return 1, lambda: app.say("{} {}".format(choice(self.ANSWER_GUESS),
                                                             self._location_to_text(utterance.context.location)))
                else:
                    return 1, lambda: app.say("{}!".format(choice(self.ANSWER_FAILED_GUESS)))

        # Set name for where we are
        else:
            for cue in self.CUE_SET_LOCATION:
                if utterance.transcript.lower().startswith(cue):
                    location = utterance.transcript.lower().replace(cue, "").strip().title()
                    utterance.context.location.label = location
                    app.brain.set_location_label(location)
                    return 1, lambda: app.say("Aha, so {}".format(self._location_to_text(utterance.context.location)))

    @staticmethod
    def _location_to_text(location):
        if location.label == location.UNKNOWN:
            return "We're in {}, {}, {}.".format(location.city, location.region, location.country)
        else:
            return "We're in {}".format(location.label)


class TimeResponder(Responder):

    DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    MONTHS = ["January", "February", "March", "April", "May", "June", "July",
              "August", "September", "October", "November", "December"]

    DATE = ["what day is it", "which day is it", "what is the date", "today"]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        for date in self.DATE:
            if date in utterance.transcript.lower():
                dt = utterance.context.datetime

                return 1, lambda: app.say("Today is {}, {} {}, {}!".format(
                    self.DAYS[dt.weekday()], self.MONTHS[dt.month-1], dt.day, dt.year
                ))


class IdentityResponder(Responder):

    CUE_ME = [
        "who are you",
        "what is your name",
    ]

    ANSWER_ME = [
        "My name is",
        "I'm",
    ]

    CUE_YOU = [
        "who am i",
        "what is my name"
    ]

    ANSWER_YOU = [
        "Your name is",
        "You are"
    ]

    @property
    def type(self):
        return ResponderType.Sensory

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
            if utterance.transcript.lower() in self.CUE_ME:
                return 1.0, lambda: app.say("{} {}!".format(choice(self.ANSWER_ME), config.NAME))

            if utterance.transcript.lower() in self.CUE_YOU:
                return 1.0, lambda: app.say("{} {}!".format(choice(self.ANSWER_YOU), utterance.chat.speaker))

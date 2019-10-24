from pepper.framework import *
#from pepper.knowledge import animations
from pepper.language import Utterance
from pepper.language.ner import NER
from .responder import Responder, ResponderType
from pepper import config

from typing import Optional, Union, Tuple, Callable


import requests

WEATHER_INTEREST = [
        #check conflict with same statement elsewhere
        "what's the weather like",
        #"what is the weather like ",
        "what's it like outside",
        #"what is it like outside ",
        "how's the weather?",
        #"how is the weather? ",
        "is it a beautiful day for a walk?",
        #"What's the weather forecast for the rest of the week?"
        #"What is the weather forecast for the rest of the week? ",
    ]
    #Similar queries unecessary. Any suggestions how to avoid this?
    #all lowercase always?


class WeatherResponder(Responder):
    def __init__(self):
        super(WeatherResponder, self).__init__()

        self._api_key = config.TOKENS["Open_Weather"]

    @property
    def type(self):
        return ResponderType.Internet

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def get_weather(self, api_key, location):
        url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
        # url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
        r = requests.get(url)
        return r.json()
        # already turns into a dictionary

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]
        # print("test")

        for cue in WEATHER_INTEREST:

            print(cue, utterance.transcript.lower())

            if utterance.transcript.lower().startswith(cue) or 'weather' in utterance.transcript.lower():

                # print ("test2")
                location = "Amsterdam"

                weather = self.get_weather(self._api_key, location)

                return 1, lambda: app.say("The weather in {} is {}, min temperature is {} and max temperature is {}"
                        .format(location, weather['weather'][0]['description'],
                        weather['main']['temp_min'],weather['main']['temp_max']))

class WeatherElserwhere(Responder):
    def __init__(self):
        super(WeatherElserwhere, self).__init__()
        # Responder.__init__(self)

        self._ner = NER()

        self._api_key = config.TOKENS["Open_Weather"]

    @property
    def type(self):
        return ResponderType.Internet

    @property
    def requirements(self):
        return [TextToSpeechComponent]

    def get_weather(self, api_key, location):
        url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
        r = requests.get(url)
        return r.json()

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        if 'weather' in utterance.tokens and 'in' in utterance.tokens:

            # Now that has weather + in check if it's a 1 or 2 word location



            print("The transcript of the utterance is")
            print(utterance.transcript)

            print("The length of the tokens of the utterance are")
            print(len(utterance.tokens))

            print("Sending the transcript to NER")

            ner = self._ner.tag(utterance.transcript)
            print(ner)

            ner_tokens = [token for token, tag in ner if tag == "LOCATION"]
            ner_location = " ".join(ner_tokens)

            print(ner_tokens, ner_location)

            location = utterance.tokens[-1]
            print("The location is: {}", location)

            weather = self.get_weather(self._api_key, location)

            print(weather)

            return 1, lambda: app.say("The weather in {} is {}".format(location, weather['weather'][0]['description']))







#class WeatherMap():
    #52.5630 and c with zoom lvl 7
    #key 4c7b59d98bcccad3ba39f5c73e28d009






















#PROGRAMMERS COMMENTS (PLEASE IGNORE)

#from pepper.framework import *
#For everything I guess

#from pepper.knowledge import Wolfram#, animations
#For wolfram and animation components

#from pepper.language import Utterance
#Need to respond an utterance?

#from .responder import Responder, ResponderType
#To define the type of responder used in this responder

#from typing import Optional, Union, Tuple, Callable
#For the type and thingy for respond, possibly returning the result as an utterance

#import re
#What's this?\



#CHeck responder obj
#Chech #type: s



#requests
#requests.get



#print(weather['main']['temp'])
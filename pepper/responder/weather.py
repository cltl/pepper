from pepper.framework import *
#from pepper.knowledge import animations
from pepper.language import Utterance
from pepper.language.ner import NER
from .responder import Responder, ResponderType
from pepper import config
from typing import Optional, Union, Tuple, Callable

import requests
import math

WEATHER_INTEREST = [
        #check conflict with same statement elsewhere (conditioned in pieks office)
        "what's the weather like",
        "what's it like outside",
        "how's the weather?",
        "is it a beautiful day for a walk?",
        #"What's the weather forecast for the rest of the week?"
    ]

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
        return r.json() # already turns into a dictionary

    def respond(self, utterance, app):
        # type: (Utterance, Union[TextToSpeechComponent]) -> Optional[Tuple[float, Callable]]

        for cue in WEATHER_INTEREST:
            print('printTEST')
            print(cue, utterance.transcript.lower())

            if utterance.transcript.lower().startswith(cue) or 'weather' in utterance.transcript.lower():

                location = "Amsterdam"

                weather = self.get_weather(self._api_key, location)

                # return 1, lambda: app.say("The weather in {} is {}, min temperature is {} and max temperature is {}"
                #         .format(location, weather['weather'][0]['description'],
                #         weather['main']['temp_min'],weather['main']['temp_max']))

                return 1, lambda: app.say("The weather in {} is {}, min temperature is {} and max temperature is {}"
                        .format(location, weather['weather'][0]['description'],
                       math.trunc(weather['main']['temp_min']), math.trunc(weather['main']['temp_max'])))


class WeatherElserwhere(Responder):
    def __init__(self):
        super(WeatherElserwhere, self).__init__()
        # Responder.__init__(self)

        self._ner = NER() #what was the name entity recognition here used for?
        self._api_key = config.TOKENS["Open_Weather"] #How did this work again? leading to config but key is in json file?

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

            print("Sending the transcript to NER")
            ner = self._ner.tag(utterance.transcript)
            print("Next Line will print the NER")
            print(ner)

            #NER parses the utterance, separating 'location' words and adding them up
            ner_tokens = [token for token, tag in ner if tag == "LOCATION"]
            ner_location = " ".join(ner_tokens)

            print("was parsed correctly, first will print tokens then location")
            print(ner_tokens, ner_location)

            print("Now will do a print test (inside weather.py)")
            weather = self.get_weather(self._api_key, ner_location)
            print(weather)
            print("printing test ended, weather.py about to end. Will return result")

            return 1, lambda: app.say("The weather  in {} is {}, min temperature is {} and max temperature is {}".format
                                      (ner_location, weather['weather'][0]['description'],
                                       math.trunc(weather['main']['temp_min']),
                                       math.trunc(weather['main']['temp_max'])))





#TODO: Implement weather map class

#class WeatherMap():
    #52.5630 and c with zoom lvl 7
    #key 4c7b59d98bcccad3ba39f5c73e28d009






















#PROGRAMMERS COMMENTS (PLEASE IGNORE)

#from typing import Optional, Union, Tuple, Callable
#For the type and thingy for respond, possibly returning the result as an utterance

#CHeck responder obj
#Chech #type: s

#requests
#requests.get

#print(weather['main']['temp'])


 #This takes the last word in utterance and saves as the location
            #location = utterance.tokens[-1]
            #print("The location is: {}", location)
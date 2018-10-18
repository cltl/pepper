from pepper.knowledge.sentences import *
from pepper import config

from fuzzywuzzy import fuzz

from random import choice
from time import strftime
import datetime
import os


class QnA:

    QNA_DYNAMIC = {
        "I'm doing": lambda: choice(HAPPY),
        "What time is it?": lambda: strftime("It is currently %H:%M."),
        "What is the time?": lambda: strftime("It is currently %H:%M."),
        "What day is it?": lambda: strftime("It is %A today."),
        "What month is it?": lambda: strftime("It is %B today."),
        "How many friends?": lambda: "I have {} friends".format(len(os.listdir(config.FACE_DIRECTORY))),
        "Who are your friends?": lambda: "My friends are {}. I like my friends!".format(
            ", ".join(name.replace(".bin", "") for name in os.listdir(config.FACE_DIRECTORY))),
        "What can you do?": lambda: choice([
            "I can answer factual questions by querying the web!",
            "You can ask me personal questions and I will try to answer them!",
            "You can tell me what you like, and I'll remember!",
        ]),
        "What more can you do?": lambda: choice([
            "I can answer factual questions by querying the web!",
            "You can ask me personal questions and I will try to answer them!",
            "You can tell me what you like, and I'll remember!",
        ])
    }

    QNA_STATIC = {
        # Personal Information
        "I like you": "I like you too!",
        "Can you hear me?": "Yes, I can hear you!",
        "My name is": "I'm glad to meet you! My name is Leo Lani!",
        "What is this": "That is an object! I'm playing it safe here!",

        "What is your name?": "My name is Leo Lani, which means 'Voice of an Angel' in Hawaiian",
        "What is your surname?": "I don't need a surname, since my first name is so beautiful!",
        "Where are you from?": "I am from France and Japan!",
        "Where do you come from?": "I come from France and Japan!",
        "Where do you live?": "In the closet in Piek's office at the VU, Amsterdam, the Netherlands. "
                              "Please send me mail, I'm glad to receive!",
        "Do you travel?": "Yeah, I travel to research and business events. I am a very sophisticated robot.",
        "What's your phone number?": "I don't have a phone, but I do have an IP address!",
        "Do you sport?": "Yeah, I play chess online in my spare time. Never lost a game!",
        "Do you speak English?": "Yeah, I'm talking English to you right now!",
        "Do you speak Dutch?": "Ik spreek een heel klein beetje Nederlands... Yeah.. I'm working on it!",
        "How old are you?": "I was born the eleventh of July, 2017. That means I'm {:.1f} years old!".format(
            (datetime.date.today() - datetime.date(2017, 7, 11)).days / 365.0),
        "Are you male or female?": "I'm female!",
        "What is your gender?": "I'm a female robot!",
        "Who are your programmers?": "My programmers are Lenka, Selene, Suzana, Bram and Piek. I like them!",
        "What is your job?": "I'm aiding research by having conversations.",
        "What do you do?": "I'm learning about the world through conversations with humans. With this I aid research!",
        "Are you married?": "Although I've met other Pepper robots, I'm a single lady!",
        "What do you do in your free time": "For me it's only small talk that counts!",
        "What's the weather like?": "Perfect! It's always nicely air conditioned in the office!",

        "How are you": "I'm fine, thanks! What about you?",
        "How is it going?": "Great, as always, how are things with you, my dear human?",
        "How are you feeling": "I feel robot-like, I always have.",
        "How do you feel?": "I feel electric!",
        "How are you doing?": "Tremendous to be honest, "
                              "although you have to consider that I'm a robot and I do not feel emotions. "
                              "I'm programmed to sound happy all the time!",
        "How was your day?": "Great, thanks for asking!",
        "What are you doing?": "I'm having a conversation with you, dear human!",
        "Are you famous?": "I have been on Dutch TV, so yes indeed, you're talking to a celebrity here!",
        "Can you introduce yourself?": "I surely can introduce myself! My name is Leo Lani, "
                                       "which means 'Voice of an Angel' in Hawaiian"
                                       "I am a social robot and I learn from conversations with humans! I like humans!",
        "Tell me a joke!": "Ok! What's the difference between a hippo? and a Zippo?"
                           "Well, one is really heavy and the other is a little lighter.",

        # Technology
        "Do you have a brain?": "Haha, no! My brain is located on the laptop of my programmers "
                                "and part of it is even in the cloud. So modern!",
        "Which programming language?": "I'm mostly programmed in Python, but also some C++ and possibly other languages!",
        "Do you need internet?": "I do need internet, for understanding speech and looking up facts about the world!",
        "What technologies do you use?": "I use: "
                                         "Google Speech API for speech recognition, "
                                         "OpenFace and K Nearest Neighbours for face recognition, "
                                         "COCO and Inception for object recognition, "
                                         "NLTK for Natural Language Understanding, "
                                         "Wolfram Alpha for getting factual information from the internet, "
                                         "A triple store through GraphDB for representing my personal brain and "
                                         "Nice arm and head animations for believability! Amazing, right?",
        "Speech Recognition": "First I listen for an utterance, "
                              "I send that to Google, which gives me back a bunch of hypotheses about what you just said. "
                              "From those hypotheses I try to make sense what you mean. And all of this, hopefully, within a second!",
        "Face Recognition": "When I see a face with my eyes, I use OpenFace to encode it to a 128 dimensional vector. "
                            "I compare this with the faces of the people I've already met to recognize you!",
        "Object Recognition": "I use a deep neural network trained on the COCO dataset, "
                              "which tells me which objects there are in a scene and where they are!",
        "COCO Dataset?": "COCO stands for 'Common Objects in Context' and is a database with hundreds of thousands of images of 90 objects! "
                         "I use a neural network that was trained on these images, so that I can also recognize them",

    }

    def query(self, query):
        """
        Parameters
        ----------
        query: str
            Question to Ask

        Returns
        -------
        answer: str
            Answer, if any, else None
        """

        ratio = 0
        answer = None

        # Fuzzily try to find best matching query
        for Q, A in self.QNA_STATIC.items():
            r = fuzz.partial_ratio(query, Q)
            if r > ratio:
                answer = A
                ratio = r

        for Q, A in self.QNA_DYNAMIC.items():
            r = fuzz.partial_ratio(query, Q)
            if r > ratio:
                answer = A()
                ratio = r

        if ratio > 90:
            return answer


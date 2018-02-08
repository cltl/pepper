from pepper.event import Event
from pepper.speech.microphone import PepperMicrophone
from threading import Thread


class WordDetectedEvent(Event):
    def __init__(self, session, callback):
        """
        Word Detected Event.

        Parameters
        ----------
        session: qi.Session
            Session to attach this event to
        callback: callable
            Function to call when event occurs
        """

        super(WordDetectedEvent, self).__init__(session, callback)

        # Connect to 'WordRecognized' event
        self._subscriber = self.memory.subscriber("WordRecognized")
        self._subscriber.signal.connect(self._on_word)

        # Subscribe to ALSpeechRecognition service. This way the events will actually be cast.
        self._detection = self.session.service("ALSpeechRecognition")
        self._detection.subscribe(self.name)

    def _on_word(self, value):
        """
        Raw Word recognized Event: convert raw event data to structured data

        Parameters
        ----------
        value: list
            Structure specified at http://doc.aldebaran.com/2-5/naoqi/audio/alspeechrecognition.html
        """
        if value:
            wordsDict = {}

            for word, confidence in zip(value[0::2], value[1::2]):
                wordsDict[word] = confidence

            self.on_word(value, wordsDict)

    def on_word(self, words, wordDict):
        """
        Word Recognized Event: callback should have identical signature

        Parameters
        ----------
        wordDict: dictionary
            dictionary with words and their confidence
        """

        self.callback(words, wordDict)

    def close(self):
        """Cleanup by unsubscribing from 'ALSpeechRecognition' service"""
        self._detection.unsubscribe(self.name)
            

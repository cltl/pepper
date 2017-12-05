from google.cloud import speech
from watson_developer_cloud import SpeechToTextV1
from pepper.speech.kaldi.client import KaldiClient
from ws4py.client.threadedclient import WebSocketClient

import urllib
import base64
import json
import sys
import re

from threading import Thread
from time import sleep, time

from enum import Enum


class Recognition(object):
    """Speech Recognition Base Class"""

    def transcribe(self, audio):
        """
        Transcribe Speech Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: list of (str, float)
            List of transcript-confidence pairs
        """
        raise NotImplementedError()


class StreamedRecognition(object):
    def __init__(self, microphone, callback):
        """
        Streamed Speech Recognition Base Class

        Parameters
        ----------
        microphone: pepper.speech.microphone.Microphone
        callback: callable
        """
        super(StreamedRecognition, self).__init__()
        self._microphone = microphone
        self._callback = callback

    @property
    def microphone(self):
        """
        Returns
        -------
        microphone: pepper.speech.microphone.Microphone
        """
        return self._microphone

    @property
    def callback(self):
        """
        Returns
        -------
        callback: callable
        """
        return self._callback

    def on_transcribe(self, hypotheses, final):
        """
        On Transcribe Event Interface

        Parameters
        ----------
        hypotheses: list of (str, float)
            List of transcript-confidence values
        final: bool
            True if transcript contains whole utterance, False if hypotheses are intermediate
        """
        self.callback(hypotheses, final)


class GoogleRecognition(Recognition):
    def __init__(self, language_code = 'en-GB', sample_rate = 16000):
        """
        Perform Speech Recognition using Google Speech API

        Parameters
        ----------
        language_code: str
            Code of the to be recognised language
        sample_rate: int
            Sample rate of audio signal
        """
        super(GoogleRecognition, self).__init__()

        self._language_code = language_code
        self._sample_rate = sample_rate

        self._config = speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = self.sample_rate,
            language_code = self._language_code,
            max_alternatives = 10
        )

    @property
    def language_code(self):
        """
        Returns
        -------
        language_code: str
            Code of the to be recognised language
        """
        return self.language_code

    @property
    def sample_rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate of audio signal
        """
        return self._sample_rate

    @property
    def config(self):
        """
        Returns
        -------
        config: speech.types.RecognitionConfig
        """
        return self._config

    def transcribe(self, audio):
        """
        Transcribe Speech Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: list of (str, float)
            List of transcript-confidence pairs
        """
        response = speech.SpeechClient().recognize(self.config, speech.types.RecognitionAudio(content=audio.tobytes()))
        hypotheses = []

        for result in response.results:
            for alternative in result.alternatives:
                hypotheses.append([alternative.transcript, alternative.confidence])

        return hypotheses


class GoogleName():
    def __init__(self, language_codes=('en-GB', 'nl-NL', 'es-ES'),
                 names=(["Lenka"], ["Piek", "Bram"], ["Selene"]),
                 sample_rate=16000):
        self._sample_rate = sample_rate

        self._config = speech.types.RecognitionConfig(
            encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language_codes[0],
            enable_word_time_offsets=True,
        )

        self._name_config = [speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = sample_rate,
            language_code = code,
            speech_contexts = [speech.types.SpeechContext(
                phrases = names[i]
            )]
        ) for i, code in enumerate(language_codes)]

        self._client = speech.SpeechClient()

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def config(self):
        return self._config
        
    @property
    def name_config(self):
        return self._name_config

    def extract(self, audio):

        PADDING = 0.5

        names = []

        words, timings = self._extract_words(audio)
        sentence = " ".join(words)

        name = re.findall(r"my name is ([a-zA-Z]+)", sentence)

        if name:
            start, end = timings[words.index(name[0])]
            print(name, start, end)

            import matplotlib.pyplot as plt

            fragment_start = int((start) * self.sample_rate)
            fragment_end = int((end + PADDING) * self.sample_rate)

            plt.plot(audio)
            plt.plot([fragment_start, fragment_end], [0,0])
            plt.show()

            fragment = audio.copy()
            fragment[:fragment_start] = 0
            fragment[fragment_end:] = 0

            for config in self.name_config:
                response = self._client.recognize(config, speech.types.RecognitionAudio(content=fragment.tobytes()))
                for result in response.results:
                    for alternative in result.alternatives:
                        if re.match(r'([A-Z].+)', alternative.transcript):
                            names.append([alternative.transcript, alternative.confidence])
        return names


    def _extract_words(self, audio):
        response = self._client.recognize(self.config, speech.types.RecognitionAudio(content=audio.tobytes()))

        words, times = [], []

        for word_info in response.results[0].alternatives[0].words:
            words.append(word_info.word)
            times.append([word_info.start_time.seconds + word_info.start_time.nanos * 1E-9,
                          word_info.end_time.seconds + word_info.end_time.nanos * 1E-9])
        return words, times


class GoogleUtterance():

    MICROPHONE_BUFFER_SECONDS = 0.1

    def __init__(self, microphone, language_code = 'en-GB', sample_rate = 16000):

        self._microphone = microphone

        self._config = speech.types.StreamingRecognitionConfig(
            config=speech.types.RecognitionConfig(
                encoding=speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
                language_code=language_code,
                sample_rate_hertz=sample_rate,
            ),
            interim_results=False,
            single_utterance=True)

        self._client = speech.SpeechClient()

    @property
    def microphone(self):
        return self._microphone

    def listen(self, seconds=60):

        requests = (speech.types.StreamingRecognizeRequest(audio_content=content.tobytes())
                    for content in self._stream_microphone())

        responses = self._client.streaming_recognize(self._config, requests)

        for response in responses:
            hypotheses = []

            for result in response.results:
                for alternative in result.alternatives:
                    hypotheses.append([alternative.transcript, alternative.confidence])

                if result.is_final:
                    return hypotheses
        return None

    def _stream_microphone(self):
        while True:
            yield self.microphone.get(self.MICROPHONE_BUFFER_SECONDS)


class GoogleStreamedRecognition(StreamedRecognition):

    BUFFER_SECONDS = 0.1

    def __init__(self, microphone, callback, language_code = 'en-GB', sample_rate = 16000):
        super(GoogleStreamedRecognition, self).__init__(microphone, callback)

        self._language_code = language_code
        self._sample_rate = sample_rate

        self._client = speech.SpeechClient()
        self._config = speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = sample_rate,
            language_code = language_code,
        )
        self._streaming_config = speech.types.StreamingRecognitionConfig(
            config = self._config,
            interim_results = True,
            single_utterance = True,
        )

        self._stopped = False

        thread = Thread(target=self.run)
        thread.setDaemon(True)
        thread.start()

    def stream_microphone(self):
        while not self._stopped:
            yield self.microphone.get(self.BUFFER_SECONDS)

    def run(self):
        requests = (speech.types.StreamingRecognizeRequest(audio_content=content.tobytes())
                    for content in self.stream_microphone())

        responses = self._client.streaming_recognize(self._streaming_config, requests)

        for response in responses:
            hypotheses = []

            for result in response.results:
                for alternative in result.alternatives:
                    hypotheses.append([alternative.transcript, 0])

                self.on_transcribe(hypotheses, result.is_final)

    def stop(self):
        self._stopped = True


    @property
    def language_code(self):
        """
        Returns
        -------
        language_code: str
            Code of the to be recognised language
        """
        return self.language_code

    @property
    def sample_rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate of audio signal
        """
        return self._sample_rate


class WatsonLanguageModel(Enum):
    ar_AR_BroadbandModel = "ar-AR_BroadbandModel"  # Modern Standard Arabic broadband model
    en_US_BroadbandModel = "en-US_BroadbandModel"  # US English broadband model
    en_GB_BroadbandModel = "en-GB_BroadbandModel"  # GB English broadband model
    es_ES_BroadbandModel = "es-ES_BroadbandModel"  # Spanish broadband model
    fr_FR_BroadbandModel = "fr-FR_BroadbandModel"  # French broadband model
    pt_BR_BroadbandModel = "pt-BR_BroadbandModel"  # Brazilian Portuguese broadband model
    zh_CN_BroadbandModel = "zh-CN_BroadbandModel"  # Mandarin broadband model
    ja_JP_BroadbandModel = "ja-JP_BroadbandModel"  # Japanese broadband model


    en_US_NarrowbandModel = "en-US_NarrowbandModel"  # US English narrowband model
    en_GB_NarrowbandModel = "en-GB_NarrowbandModel"  # GB English narrowband model
    es_ES_NarrowbandModel = "es-ES_NarrowbandModel"  # Spanish narrowband model
    ja_JP_NarrowbandModel = "ja-JP_NarrowbandModel"  # Japanese narrowband model
    pt_BR_NarrowbandModel = "pt-BR_NarrowbandModel"  # Brazilian Portuguese narrowband model
    zh_CN_NarrowbandModel = "zh-CN_NarrowbandModel"  # Mandarin narrowband model


class WatsonRecognition(Recognition):
    def __init__(self, model = WatsonLanguageModel.en_GB_BroadbandModel, sample_rate = 16000):
        """
        Perform Speech Recognition using the Watson API

        Parameters
        ----------
        model: WatsonLanguageModel
            Language model to use for speech recognition
        sample_rate: int
            Sample rate of audio signal
        """

        self._model = model
        self._sample_rate = sample_rate

        self.stt = SpeechToTextV1(
            username="d3977008-2079-42f8-ba77-8b44213a4c48",
            password="7I8oVN4aboFm"
        )

        self.stt.get_model(model.value)

    @property
    def model(self):
        """
        Returns
        -------
        model: WatsonLanguageModel
            Model to use for speech recognition
        """
        return self._model

    @property
    def sample_rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate of audio signal
        """
        return self._sample_rate

    def transcribe(self, audio):
        """
        Transcribe Speech Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: list of (str, float)
            List of transcript-confidence pairs
        """
        response = self.stt.recognize(audio.tobytes(),
                                      content_type='audio/l16;rate={}'.format(self.sample_rate),
                                      max_alternatives=10)

        transcript_confidence = []

        confidence = 0

        for alternative in response['results'][0]['alternatives']:
            if 'confidence' in alternative:
                confidence = alternative['confidence']

            transcript_confidence.append([alternative['transcript'], confidence])

        return transcript_confidence


class WatsonStreamedRecognition(WebSocketClient, StreamedRecognition):

    API_URL = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
    API_USR = "d3977008-2079-42f8-ba77-8b44213a4c48"
    API_PSS = "7I8oVN4aboFm"

    BUFFER_SECONDS = 1

    def __init__(self, microphone, callback, model = WatsonLanguageModel.en_GB_BroadbandModel, sample_rate = 16000):
        """
        Perform Streamed Speech Recognition using the Watson API

        Parameters
        ----------
        microphone: SystemMicrophone
            Microphone to Listen to
        callback: callable
            Callback to call on transcribe
        model: WatsonLanguageModel
            Language model to use for speech recognition
        sample_rate: int
            Sample rate of audio signal
        """

        StreamedRecognition.__init__(self, microphone, callback)
        WebSocketClient.__init__(self, r"{}?model={}".format(self.API_URL, model.value),
                                 headers=[("Authorization", "Basic {}".format(
                                     base64.encodestring("{}:{}".format(self.API_USR, self.API_PSS))))])

        self._sample_rate = sample_rate
        self._listening = False
        self.connect()

    @property
    def sample_rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate of audio signal
        """
        return self._sample_rate

    def opened(self):
        """Called after connecting to Watson API, sets up connection and starts microphone stream"""

        self.send(json.dumps({
            "action": "start",
            "content-type": "audio/l16;rate={}".format(self.sample_rate),
            "interim_results": True,
            "max_alternatives": 10,

        }))

        self.stream_thread = Thread(target=self.stream_microphone)
        self.stream_thread.setDaemon(True)
        self.stream_thread.start()

    def stream_microphone(self):
        """Stream Microphone Signal to Server"""
        try:
            while True:
                signal = self.microphone.get(self.BUFFER_SECONDS)
                self.send(signal.tobytes(), binary=True)
        except AttributeError as e:
            print >> sys.stderr, "{} has timed out.".format(self.__class__.__name__)

    def received_message(self, message):
        """Called on response from Watson API Server, calls callback function"""

        message = json.loads(str(message))

        if 'results' in message:
            hypotheses = []
            confidence = 0

            for alternative in message['results'][0]['alternatives']:
                if 'confidence' in alternative:
                    confidence = alternative['confidence']

                hypotheses.append([alternative['transcript'], confidence])
            self.on_transcribe(hypotheses, message['results'][0]['final'])


class KaldiRecognition(Recognition):
    def __init__(self, url = r"ws://localhost:8080/client/ws/speech", sample_rate = 16000):
        """
        Perform Kaldi Recognition using Locally Running Kaldi Server

        Parameters
        ----------
        url: str
            Address of Kaldi Server
        sample_rate: int
            Sample rate of audio signal
        """
        super(KaldiRecognition, self).__init__()

        self._url = url
        self._sample_rate = sample_rate

    @property
    def url(self):
        """
        Returns
        -------
        url: str
            Address of Kaldi Server
        """
        return self._url

    @property
    def sample_rate(self):
        """
        Returns
        -------
        sample_rate: int
            Sample rate of audio signal
        """
        return self._sample_rate

    def transcribe(self, audio):
        """
        Transcribe Speech Audio

        Parameters
        ----------
        audio: numpy.ndarray

        Returns
        -------
        hypotheses: list of (str, float)
            List of transcript-confidence pairs
        """
        client = KaldiClient(self.url, audio, self.sample_rate)
        client.connect()
        transcript = client.transcript
        client.close_connection()
        return transcript


class KaldiStreamedRecognition(WebSocketClient, StreamedRecognition):

    BUFFER_SECONDS = 0.25

    def __init__(self, microphone, callback, url = r"ws://localhost:8080/client/ws/speech"):
        """
        Perform Streamed Speech Recognition using local Kaldi Server

        Parameters
        ----------
        microphone: SystemMicrophone
            Microphone to Listen to
        callback: callable
            Callback to call on transcribe
        url: str
            URL of Kaldi Server
        """

        StreamedRecognition.__init__(self, microphone, callback)
        WebSocketClient.__init__(self,
                    "{}?{}".format(url, urllib.urlencode([("content-type", (
                    "audio/x-raw, "
                    "layout=(string)interleaved, "
                    "rate=(int){}, "
                    "format=(string)S16LE,"
                    "channels=(int){}".format(microphone.rate, microphone.channels)))])))

        self.connect()

    def opened(self):
        """Called after connecting to Kaldi Server, starts microphone stream"""

        thread = Thread(target=self.stream_microphone)
        thread.start()

    def stream_microphone(self):
        """Stream Microphone Signal to Server"""

        while True:
            signal = self.microphone.get(self.BUFFER_SECONDS)
            self.send(signal.tobytes(), binary=True)

    def received_message(self, message):
        """Called on response from Kaldi Server, calls callback function"""

        message = json.loads(str(message))

        if not message['status']:
            if 'result' in message:
                hypotheses = []
                likelihood = 0

                for hypothesis in message['result']['hypotheses']:
                    if 'likelihood' in hypothesis:
                        likelihood = hypothesis['likelihood']/100

                    hypotheses.append([hypothesis['transcript'], likelihood])

                self.on_transcribe(hypotheses, message['result']['final'])

        else:
            if 'message' in message:
                print >> sys.stderr, "Kaldi Error ({}) {}".format(message['status'], message['message'])
            else:
                print >> sys.stderr, "Kaldi Server Error ({})".format(message['status'])


if __name__ == "__main__":
    from pepper.speech.microphone import SystemMicrophone
    from pepper.knowledge.wolfram import Wolfram


    # Watson Streaming Recognition Example
    def on_speech(hypotheses, final):
        question = "\rQ: {}".format(hypotheses[0][0])

        if final:
            print "{}?".format(question)
            answer = Wolfram().query(question)
            if answer:
                print "A: {}\n".format(answer)
            else:
                print "\r",
        else:
            print question,

    recognition = GoogleStreamedRecognition(SystemMicrophone(), on_speech)
    print("Recognition Booted!")

    sleep(15)
    recognition.stop()

    # # Recognition Example (Google vs Kaldi vs Watson)
    # # Next to having the Kaldi GStreamer Server set up, you should also have access to the Google Speed API,
    # # See: https://cloud.google.com/speech/
    #
    # from pepper.speech.microphone import SystemMicrophone
    # from time import time
    #
    # for i in range(1, 4):
    #     print(i)
    #     sleep(1)
    # print("Talk!")
    #
    # audio = SystemMicrophone().get(5)
    #
    # print("Thank You, Processing!\n")
    #
    # try:
    #
    #     t0 = time()
    #     hypotheses = GoogleRecognition().transcribe(audio)
    #     print("Google ({:1.3f}s)".format(time() - t0))
    #
    #     for i, hypothesis in enumerate(hypotheses):
    #         print(u"\t{:>2d}. [{:3.0%}] {}".format(i+1, *hypothesis[::-1]))
    #
    #     t0 = time()
    #     hypotheses = KaldiRecognition().transcribe(audio)
    #     print("Kaldi ({:1.3f}s)".format(time() - t0))
    #
    #     for i, hypothesis in enumerate(hypotheses):
    #         print(u"\t{:>2d}. [{:3.0%}] {}".format(i+1, *hypothesis[::-1]))
    #
    #     t0 = time()
    #     hypotheses = WatsonRecognition().transcribe(audio)
    #     print("Watson ({:1.3f}s)".format(time() - t0))
    #
    #     for i, hypothesis in enumerate(hypotheses):
    #         print(u"\t{:>2d}. [{:3.0%}] {}".format(i+1, *hypothesis[::-1]))
    #
    # except AttributeError:
    #     pass

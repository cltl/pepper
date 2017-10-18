from google.cloud import speech

from ws4py.client.threadedclient import WebSocketClient
from threading import Thread
import urllib
from time import sleep, strftime
import json
import sys


class Recognition(object):
    def transcribe(self, audio):
        raise NotImplementedError()


class StreamedRecognition(object):
    def __init__(self, microphone, callback):
        """
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

    def on_transcribe(self, hypotheses):
        self.callback(hypotheses)


class GoogleRecognition(Recognition):
    def __init__(self, sample_rate = 16000, language_code = 'en-GB'):
        super(GoogleRecognition, self).__init__()

        self._sample_rate = sample_rate
        self._language_code = language_code

        self._config = speech.types.RecognitionConfig(
            encoding = speech.enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz = self.sample_rate,
            language_code = self._language_code,
            max_alternatives = 10
        )

    @property
    def sample_rate(self):
        return self._sample_rate

    @property
    def language_code(self):
        return self.language_code

    @property
    def config(self):
        return self._config

    def transcribe(self, audio):
        response = speech.SpeechClient().recognize(self.config, speech.types.RecognitionAudio(content=audio.tobytes()))
        transcript_confidence = []

        for result in response.results:
            for alternative in result.alternatives:
                transcript_confidence.append([alternative.transcript, alternative.confidence])

        return transcript_confidence


class KaldiRecognitionClient(WebSocketClient):
    def __init__(self, url, audio):
        super(KaldiRecognitionClient, self).__init__(url)

        self._audio = audio
        self._transcript_confidence = []

    @property
    def audio(self):
        return self._audio

    @property
    def transcript(self):
        while not self._transcript_confidence: sleep(0.1)
        return self._transcript_confidence

    def opened(self):
        self.send(self.audio.tobytes(), binary=True)
        self.send("EOS")

    def received_message(self, message):
        response = json.loads(str(message))

        if not response['status']:
            if 'result' in response:
                if response['result']['final']:
                    transcript_confidence = []

                    for hypothesis in response['result']['hypotheses']:
                        transcript_confidence.append([hypothesis['transcript'], hypothesis['likelihood']/100])
                    self._transcript_confidence = transcript_confidence
        else:
            if 'message' in response:
                print >> sys.stderr, "Kaldi Error ({}) {}".format(response['status'], response['message'])
            else:
                print >> sys.stderr, "Kaldi Server Error ({})".format(response['status'])


class KaldiRecognition(Recognition):
    def __init__(self, url = r"ws://localhost:8080/client/ws/speech", sample_rate = 16000):
        super(KaldiRecognition, self).__init__()

        self._request = "{}?{}".format(url, urllib.urlencode([("content-type",(
            "audio/x-raw, layout=(string)interleaved, rate=(int){}, format=(string)S16LE, channels=(int)1".format(
                sample_rate
            )
        ))]))

    @property
    def request(self):
        return self._request

    def transcribe(self, audio):
        client = KaldiRecognitionClient(self.request, audio)
        client.connect()
        transcript = client.transcript
        client.close_connection()
        return transcript


class StreamedKaldiRecognition(WebSocketClient, StreamedRecognition):

    BUFFER_SECONDS = 0.25

    def __init__(self, microphone, callback, url = r"ws://localhost:8080/client/ws/speech"):
        WebSocketClient.__init__(self,
             "{}?{}".format(url, urllib.urlencode([("content-type", (
                 "audio/x-raw, "
                 "layout=(string)interleaved, "
                 "rate=(int){}, "
                 "format=(string)S16LE,"
                 "channels=(int){}".format(
                     microphone.rate, microphone.channels)
             ))])))
        StreamedRecognition.__init__(self, microphone, callback)

    def start(self):
        self.connect()

        while True:
            sleep(1)

    def opened(self):
        def stream_microphone():
            while True:
                self.send(self.microphone.get(self.BUFFER_SECONDS).tobytes(), binary=True)

        thread = Thread(target=stream_microphone)
        thread.start()

    def received_message(self, message):
        response = json.loads(str(message))

        if not response['status']:
            if 'result' in response:
                if response['result']['final']:
                    hypotheses = []

                    for hypothesis in response['result']['hypotheses']:
                        hypotheses.append([hypothesis['transcript'], hypothesis['likelihood']/100])

                    self.on_transcribe(hypotheses)

        else:
            if 'message' in response:
                print >> sys.stderr, "Kaldi Error ({}) {}".format(response['status'], response['message'])
            else:
                print >> sys.stderr, "Kaldi Server Error ({})".format(response['status'])


if __name__ == "__main__":
    # ..:: Live Speech Recognition Example ::..
    # This code uses the Kaldi GStreamer server, and assumes it is running at ws://localhost:8080/client/ws/speech
    # See: https://github.com/alumae/kaldi-gstreamer-server
    # Installing The GStreamer server as a Docker image is probably easiest, see:
    # https://github.com/jcsilva/docker-kaldi-gstreamer-server
    # TODO: Fix all bugs/crashes (This is by no means stable (yet)!)
    # TODO: Fix Kaldi Confidence Score (Goes above 100%?)

    from pepper.speech.microphone import SystemMicrophone
    def on_transcribe(hypotheses):
        print("[{}][{:3.0%}] {}".format(strftime("%H:%M:%S"), *hypotheses[0][::-1]))
    recognition = StreamedKaldiRecognition(SystemMicrophone(), on_transcribe)
    recognition.start()

    # # Offline Recognition Example (Google vs Kaldi)
    # # Next to having the Kaldi GStreamer Server set up, you should also have access to the Google Speed API,
    # # See: https://cloud.google.com/speech/
    # from pepper.speech.microphone import SystemMicrophone
    # from time import time
    #
    # for i in range(1, 4):
    #     print(i)
    #     sleep(1)
    # print("Talk!")
    #
    # audio = SystemMicrophone().get(4)
    #
    # print("Thank You, Processing!\n")
    #
    # t0 = time()
    # hypotheses = GoogleRecognition().transcribe(audio)
    # print("Google ({:1.3f}s)".format(time() - t0))
    #
    # for i, hypothesis in enumerate(hypotheses):
    #     print(u"\t{:>2d}. [{:3.0%}] {}".format(i+1, *hypothesis[::-1]))
    #
    # t0 = time()
    # hypotheses = KaldiRecognition().transcribe(audio)
    # print("Kaldi ({:1.3f}s)".format(time() - t0))
    #
    # for i, hypothesis in enumerate(hypotheses):
    #     print(u"\t{:>2d}. [{:3.0%}] {}".format(i+1, *hypothesis[::-1]))

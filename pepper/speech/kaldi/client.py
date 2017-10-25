from ws4py.client.threadedclient import WebSocketClient
from time import sleep
import urllib
import json
import sys


class KaldiClient(WebSocketClient):
    def __init__(self, url, audio, sample_rate):
        super(KaldiClient, self).__init__(
            "{}?{}".format(url, urllib.urlencode([("content-type", (
                "audio/x-raw,"
                "layout=(string)interleaved,"
                "rate=(int){},"
                "format=(string)S16LE,"
                "channels=(int)1".format(
                    sample_rate
                )
            ))]))
        )

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
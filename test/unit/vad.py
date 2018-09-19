from pepper.sensor.vad import VAD
from pepper import config

from test.unit.microphone import MicrophoneTest, SystemMicrophoneTest, NaoqiMicrophoneTest


class VADTest(MicrophoneTest):
    def __init__(self):
        MicrophoneTest.__init__(self)
        self._vad = VAD(self.microphone, [self.on_utterance])

        print("VAD | Voice: activation > {:3.2f} | Non Voice: activation < {:3.2f}".format(
            config.VAD_VOICE_THRESHOLD, config.VAD_NONVOICE_THRESHOLD))

    def on_audio(self, audio):
        super(VADTest, self).on_audio(audio)
        print "| VAD {} (activation: {:3.2f})".format("VOICE: {:3.2f}s".format(
            len(self._vad._voice_buffer) / (2 * float(self.microphone.rate))) if self._vad._voice else "NO VOICE",
                                                      self._vad.activation()),

    def on_utterance(self, audio):
        pass


class SystemVADTest(VADTest, SystemMicrophoneTest):
    def __init__(self):
        SystemMicrophoneTest.__init__(self)
        VADTest.__init__(self)


class NaoqiVADTest(VADTest, NaoqiMicrophoneTest):
    def __init__(self):
        NaoqiMicrophoneTest.__init__(self)
        VADTest.__init__(self)


if __name__ == '__main__':
    if config.APPLICATION_TARGET == config.ApplicationTarget.SYSTEM:
        SystemVADTest().run()
    elif config.APPLICATION_TARGET == config.ApplicationTarget.NAOQI:
        NaoqiVADTest().run()

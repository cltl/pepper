from pepper import SystemMicrophone, Utterance, GoogleRecognition
from time import sleep


recognition = GoogleRecognition()


def on_utterance(audio):
    print(recognition.transcribe(audio))


SAMPLE_RATE = 16000
microphone = SystemMicrophone(SAMPLE_RATE, 1)
utterance = Utterance(microphone, on_utterance)
utterance.start()

print("Utterance Test Started")

while True:
    sleep(1)

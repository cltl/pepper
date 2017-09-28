# # Text Input
# from pepper.knowledge.wolfram import *
#
# wolfram = Wolfram([WordDefinitionHandler()])
#
# while True:
#     print("A: {}\n".format(wolfram.get(raw_input("Q: "))))


from pepper.speech.microphone import SystemMicrophone
from pepper.speech.recognition import GoogleRecognition
from pepper.knowledge.wolfram import SimpleWolfram

wolfram = SimpleWolfram()

def on_transcribe(transcript, confidence):
    print(u"Q: {} [{:3.0%}]".format(transcript, confidence))
    print(u"A: {}\n".format(wolfram.get(transcript)))

recognition = GoogleRecognition(SystemMicrophone(), on_transcribe).run()


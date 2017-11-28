from pepper.speech.recognition import GoogleName, GoogleRecognition
from pepper.speech.microphone import SystemMicrophone
import numpy as np

# for name, confidence in GoogleName().extract(np.fromfile('tmp.raw', np.int16)):
#     print("{:20s} {:3.0%}".format(name, confidence))


print("Talk!")
for name, confidence in GoogleName().extract(SystemMicrophone().get(5)):
    print("{:20s} {:3.0%}".format(name, confidence))
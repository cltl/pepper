CLTL Pepper/Nao Repository
--------------------------

This is the (WIP) repository for CLTL Pepper/Nao Applications.

#### (To Be Implemented) Features
- [x] Object-Oriented wrapper around nao(qi)
- [x] Creating apps that run both on the robot and on host machine
- [ ] Framework for creating BDI applications
- [ ] Machine Learning necessary for Human-Robot conversation
- [ ] Realtime (interactive?) visualisation of BDI state in web browser


#### Installation

##### 0: Python 2.7 (32-bit Windows / 64-bit Linux)
The CLTL Pepper/Nao Repository is dependent on the ``Naoqi Python SDK`` by Softbank Robotics,
which is only available for 32-bit Python 2.7 on Windows and 64-bit Python 2.7 on Linux.

##### 1: Naoqi Python SDK by Softbank Robotics
This project builds onto the ``Naoqi Python SDK`` by SoftBank Robotics.
Please refer to their [install guide](http://doc.aldebaran.com/2-5/dev/python/install_guide.html) for more information.
Please make sure the ``PYTHONPATH`` environment variable reflects the location of the SDK and you're using Python 2.7!

##### 3: Google Cloud Speech-to-Text
The [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text/) is used as Speech Recognition solution for this project.
Please refer to their website for licencing and installation instructions.
It is of course possible to use a different Automatic Speech Recognition (ASR) solution, if you wish!

##### 4: OpenFace (Docker)
Face recognition in this project is done using the open source OpenFace project ([Site](http://cmusatyalab.github.io/openface/), [Git](https://github.com/cmusatyalab/openface)),
which is, to put it mildly, difficult to install; Probably even impossible on Windows.
Luckily, the developers were so kind to provide a [Docker](https://www.docker.com/) image, which can be obtained using `docker pull bamos/openface`.
If you're planning to run Docker on a Windows machine, make sure you have Windows Pro/Enterprise!

##### 5: Object Recognition (Pepper Tensorflow)
In order to use the [Inception](https://www.tensorflow.org/tutorials/images/image_recognition) and [COCO](cocodataset.org/) models natively within this project,
you need to clone pepper's sister-project: [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow), which includes the Tensorflow services within Python 3.6.
These services need to run as a separate process either locally or remotely next to the main application.
Since Tensorflow requires Python 3, this is our way of using Tensorflow in an otherwise Python 2.7 repo.

##### 6: Other Python Dependencies
This project depends on ``numpy``, ``OpenCV (cv2)``, ``pyaudio`` and ``webrtcvad``.
Most of these packages can be installed using ``pip``,  with one notable exception being ``OpenCV``,
which needs to be [downloaded](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_setup/py_table_of_contents_setup/py_table_of_contents_setup.html) and build manually (Windows binaries exist).


#### Structure

##### 1: Apps & Events
This package revolves around _Apps_, which program some robot behaviour.
_Apps_ provide events for each sensory experience the robot 'perceives'. These events are (thus far):
- ``on_image`` for every frame captured by robot camera
- ``on_object`` for each object detected in a camera frame
- ``on_face`` for each face detected in a camera frame
- ``on_face_known`` when detected face is 'known' to the robot
- ``on_face_new`` when detected face is 'new' to the robot
- ``on_audio`` for every frame of audio captured by robot microphone
- ``on_utterance`` for every segmented piece of speech-audio
- ``on_transcript`` for every utterance that can be resolved into text

More events are sure to come in the future!

##### 2: Platforms & Devices

In order to run _Apps_ made with this framework on multiple platforms, abstractions have been made for all host specific devices:
- ``AbstractCamera``
- ``AbstractMicrophone``
- ``AbstractTextToSpeech``

Implementations have been made for Naoqi Platforms, using the Camera/Microphone/AnimatedSpeech from Pepper/Nao,
and for Laptop/PC Platforms (tested on Windows), using the built in Webcam/Microphone/Console instead.
It should be possible to extend this to other devices later on, as well.
being able to run applications on your host device gives the advantage that you can test the application without needing the robot.

In order to create an application, one needs to create a class that inherits from the Application of the target platform.
These can be easily switched around, as is demonstrated below:

```python
from pepper.framework.naoqi import NaoqiApp
from pepper.framework.system import SystemApp

APP = NaoqiApp or SystemApp

class MyApp(APP):
    def on_transcript(self, transcript):
        self.text_to_speech.say("Right you are!")
        
if __name__ == '__main__':
    MyApp().start()
```

##### 3: Intentions

When Applications get bigger, the need for more structure arises. That is where _Intentions_ come in.
Within each _App_, the user programs one or several _Intentions_ (The 'I' in [BDI](https://en.wikipedia.org/wiki/Belief–desire–intention_software_model)).
These intentions act as subgoals within each application. An example is demonstrated below.

```python
from pepper.framework.system import SystemApp
from pepper.framework import AbstractIntention


class IdleIntention(AbstractIntention):
    def on_face_new(self, bounds, face):
        self.app.intention = MeetNewPersonIntention()
        

class MeetNewPersonIntention(AbstractIntention):
    def __init__(self):
        super(MeetNewPersonIntention, self).__init__()
        self.text_to_speech.say("What is your name?")
        
    def on_transcript(self, transcript):
        self.text_to_speech.say("Nice to meet you!")
        self.app.intention = IdleIntention()
        
if __name__ == '__main__':
    SystemApp(IdleIntention()).start()
```

#### Running

To run an application, you'll have to run a few services and take a few considerations first.

##### 1: Docker

Please Run Docker (and make sure you've pulled ``bamos/openface``, see _Installation_ for details).
The docker image will be started automatically and keep active, when running an application for the first time.
When you're done running applications and you don't need the OpenFace service anymore,
please start up a terminal and run ``docker stop openface``.
This can also help when experiencing issues with Docker, which sometimes occurs when it starts automatically with the OS.
In that the classic _reboot-and-try-again_ scheme works wonders.

##### 2: COCO Client

In order to do object detection, we make use of a COCO model within Tensorflow.
A COCO service has been implemented in and can be run from the [pepper_tensorflow](https://github.com/cltl/pepper_tensorflow) project.
Simply run ```python3 pepper_tensorflow/coco.py``` and the service will boot.

##### 3: Face Data

In oder to make face recognition possible, the ``people`` directory needs to be populated with face-data.
The files should be named ``<Name of Person>.bin`` and contain 1 or more 128-dimensional vectors of the person's face.
Due to privacy concerns, faces have not been included in the Git repo. These vectors are provided with the ``on_face`` event.

##### 4: Config

The global config file can be found under ``pepper/config.py``. Please modify this to your (performance) needs!

##### 5: Running a (test) application

Running ``test/vebose_app.py``, will print out which events fire when and with what data.
If you manage to run this without any errors all dependencies are installed correctly and other apps should work too!

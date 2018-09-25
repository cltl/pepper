CLTL Pepper/Nao Repository
--------------------------

This is the (WIP) repository for CLTL Pepper/Nao Applications.

#### Features
- [x] Object-Oriented wrapper around nao(qi)
- [x] Creating apps that run both on the robot and on host machine
- [x] Framework for creating BDI applications
- [x] Machine Learning necessary for Human-Robot conversation
- [ ] Realtime (interactive?) visualisation of BDI state in web browser


#### Installation

Unfortunately, this project has a lot of components and therefore a lot of dependencies.
Yet, we have tried our best to make an extensive and comprehensive installation guide:

Steps 1/2 -> Only necessary when using Naoqi to interact with Pepper/Nao robots. 

##### 1: Python 2.7 (32-bit Windows / 64-bit Linux)
The CLTL Pepper/Nao Repository is dependent on the ``Naoqi Python SDK`` by Softbank Robotics,
which is only available for 32-bit Python 2.7 on Windows and 64-bit Python 2.7 on Linux.

##### 2: Naoqi Python SDK by Softbank Robotics
This project builds onto the ``Naoqi Python SDK`` by SoftBank Robotics.
Please refer to their [install guide](http://doc.aldebaran.com/2-5/dev/python/install_guide.html) for more information.
Please make sure the ``PYTHONPATH`` environment variable reflects the location of the SDK and you're using Python 2.7!

##### 3: Google Cloud

This projects makes use of Google Cloud services for speech recognition/production.
This is a paid service, although a trail for a free year is available.
After following instructions to make a cloud project on their [website](https://cloud.google.com/speech-to-text/docs/quickstart-client-libraries),
download your key as ``google_cloud_key.json`` and place it in the root of this project.

###### 3a. Speech-To-Text
The [Google Cloud Speech-to-Text API](https://cloud.google.com/speech-to-text/) is used as Speech Recognition solution for this project.
Please refer to their website for licencing and installation instructions.
It is of course possible to use a different Automatic Speech Recognition (ASR) solution, if you wish!
Call ``pip install google-cloud-speech`` in order to install the required Python libraries.

###### 3b. Text-To-Speech
The [Google Cloud Text-To-Speech API](https://cloud.google.com/text-to-speech/) is used a Text to Speech solution
when running applications on your PC.
Please, again, refer to their website for licencing and installation instructions.
Call ``pip install google-cloud-TextToSpeech playsound`` in order to install the required Python libraries.

If your platform happens to be Mac, and the ``playsound`` installation complains about the ``cairo`` dependency,
try running ``pip install -U PyObjC``.

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

##### 6: Natural Language Understanding
For analyzing utterances, this project relies on [NLTK](https://www.nltk.org/). Make sure to install this library and download ``averaged_perceptron_tagger`` and ``wordnet``.
For Named Entity Recognition, you need to have Java installed on your machine. Please make sure it is callable from the command line.

##### 7: Knowledge representation (Brain)
In this project, knowledge is represented in the form of triples and stored in a triple store. As such, you need to install ``rdflib``, ``iribaker``, and ``SPARQLWrapper`` via pip. 
Additionally, you have to install [GraphDB](http://graphdb.ontotext.com/). Please follow the instructions to download, the free version will suffice. 

GraphDB's UI can be accessed through ``http://localhost:7200/``. From the UI, you will need to set up a new repository called _leolani_. Don't forget to connect to the repository when you start GraphDB.

##### 8: Wolfram Alpha
This project makes use of the [Wolfram Alpha Spoken Results API](https://products.wolframalpha.com/spoken-results-api/documentation/)
A free (academic) licence is available that allows 2000 queries a month (which is plenty, in our experience).
Please create a file ``tokens.json``, which the following information to the root of this project:

```
{
  "wolfram": <YOUR KEY>
}
```


##### 9: Other Python Dependencies
The project requirements are listed in ```requirements.txt``` and can be installed via pip.

On Windows, an OpenCV binary needs to be [downloaded](https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_setup/py_table_of_contents_setup/py_table_of_contents_setup.html).
pip ```opencv-python``` will be sufficient for MacOS platforms.


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
and for Laptop/PC Platforms (tested on Windows and Mac), using the built in Webcam/Microphone/Console instead.
It should be possible to extend this to other devices later on, as well.
Being able to run applications on your host device gives the advantage that you can test the application without needing the robot.

In order to create an application, one needs to create a class that inherits from the Application of the target platform.
These can be easily switched around, as is demonstrated below:

```python
from pepper.framework.naoqi import NaoqiApp
from pepper.framework.system import SystemApp

APP = NaoqiApp or SystemApp

class MyApp(APP):
    def on_transcript(self, transcript, audio):
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
        
    def on_transcript(self, transcript, audio):
        self.text_to_speech.say("Nice to meet you!")
        self.app.intention = IdleIntention(self.app)
        
if __name__ == '__main__':
    # Boot Application
    app = SystemApp()  # Run on PC

    # Boot Intention
    intention = IdleIntention(app)

    # Link (Default) Intention to App
    app.intention = intention

    # Start App (a.k.a. Start Microphone and Camera)
    app.start()
```

##### 4: Structured data
In order to store knowledge in the brain, we need to parse unstructured natural language and transform it to triples.
For this purpose, and following [GRaSP](https://github.com/cltl/GRaSP), we have designed a _json_ template that allows us to transmit this information between modules. 


```json
{
  "subject": {
    "id": "str: URI for this instance",
    "label": "str: label to refer to this instance (lower case)",
    "type": "str: one of leolani's 35 classes, or similar", 
    "confidence": "float: value between 0-1",
    "position": "str: beginPosition-endPosition"
  },
  "predicate": {
    "type": "str: one of leolani's 21 predicates, or similar", 
    "confidence": "float: value between 0-1",
    "position": "str: beginPosition-endPosition"
  },
  "object": {
    "id": "str: URI for this instance",
    "label": "str: label to refer to this instance (lower case)",
    "type": "str: one of leolani's 35 classes, or similar", 
    "confidence": "float: value between 0-1",
    "position": "str: beginPosition-endPosition"
  },
  "output_meta": {
    "type": "categorical: [subject, predicate, object]",
    "format": "categorical: [list, bool]"
  },
  "input_meta": {
    "raw": "str: original input parsed/sensed (transcript or image)",
    "type": "categorical: [statement, question, experience]",
    "author": "str: label of person producing the input",
    "chat": "str: chat ID",
    "turn": "str: turn ID",
    "date": "datestamp: date when input was produced",
    "attributions": {
      "certainty": "categorical: [certain, possible, probable, underspecified]",
      "sentiment": "categorical: [negative, positive]",
      "emotion": "categorical: [anger, disgust, fear, happiness, sadness, surprise]"
    }
  }
}
```

###### Considerations
* Entity/Predicate types (subject and objects): In general, recognized/parsed ``types`` are the ones present in the ontology. However, it is also possible to have unknown types, in which case these types will be created in the ontology.
* Case folding: All fields (type, label, author, and attribution) should be lowercase, except for ``raw``. [Snake case](https://en.wikipedia.org/wiki/Snake_case) (replacing spaces with underscores) should be also followed when needed.
* Positions: It is necessary to keep track of where in the raw input was the subject/predicate/object mentioned. As such, for an utterance as 'Piek likes pizza' should return ``positions`` like '0-3', '5-9' and '11-15' respectively.
* Entity URI: Use full valid URIs for IDs (i.e. http://cltl.nl/leolani/world/piek)


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
Simply run ```pepper_tensorflow/coco.py``` (using Python 3) and the service will boot.

##### 3: Face Data

In oder to make face recognition possible, the ``people`` directory needs to be populated with face-data.
The files should be named ``<Name of Person>.bin`` and contain 1 or more 128-dimensional vectors of the person's face.
Due to privacy concerns, faces have not been included in the Git repo. These vectors are provided with the ``on_face`` event.

##### 4: Config

The global config file can be found under ``pepper/config.py``. Please modify this to your (performance) needs!

##### 5: Running a (test) application

Running ``test/vebose_app.py``, will print out which events fire when and with what data.
If you manage to run this without any errors all dependencies are installed correctly and other apps should work too!

HowTo's
-------

#### How To Boot

1. Start GraphDB Free

2. Start Docker

3. Start COCO (pepper_tensorflow - coco.py - ctrl-shift-F10)

4. Start any app (e.g. ``pepper/intention/reactive.py``)

Enjoy (& Check settings/IP's in ``pepper/config.py``)!


#### How to switch between PC/Robot Host

- for Robot
```python
from pepper.framework.naoqi import NaoqiApp
app = NaoqiApp()
```
- for PC
```python
from pepper.framework.system import SystemApp
app = SystemApp()
```

Common Issues
-------------

- **I receive some error related to Docker/OpenFace**
    - Reboot Docker & try again! :)
- **Microphone samples are dropped / stuff is slow on the robot!!**
    - Make sure network is as optimal as can be
    - Tweak ``CAMERA_RESOLUTION`` & ``CAMERA_FRAMERATE`` in ``pepper/config.py``
- **Robot has weird (or local) IP**
    - Reboot robot and hope for the best!



"""
Sensor
======

The framework.sensor package implements Face, Object and Speech Recognition:

- :class:`~pepper.framework.sensor.vad.VAD` implements Voice Activity Detection on Microphone input
- :class:`~pepper.framework.sensor.asr.StreamedGoogleASR` implements Automated Speech Recognition through Google Speech API
- :class:`~pepper.framework.sensor.obj.ObjectDetectionClient` connects to pepper_tensorflow_ for Object Detection
- :class:`~pepper.framework.sensor.face.OpenFace` connects to the `bamos/openface` Docker container for Face Recognition
- :class:`~pepper.framework.sensor.location.Location` gets the current geographical location (WIP)
"""

from .asr import AbstractASR, GoogleTranslator, UtteranceHypothesis, SynchronousGoogleASR, StreamedGoogleASR
from .obj import Object, ObjectDetectionClient, ObjectDetectionTarget
from .face import OpenFace, FaceStore, FaceClassifier, Face
from .obj import Object
from .vad import VAD
from .obj import Object

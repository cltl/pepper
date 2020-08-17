"""
The Pepper Framework Package consists out of the basic building blocks to make robot applications.

Abstract
========

The framework.abstract package contains specifications for:


- Sensors: :class:`~pepper.framework.abstract.camera.AbstractCamera` :class:`~pepper.framework.abstract.microphone.AbstractMicrophone`
- Actuators: :class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech` :class:`~pepper.framework.abstract.motion.AbstractMotion` :class:`~pepper.framework.abstract.led.AbstractLed`
- Backends & Applications: :class:`~pepper.framework.abstract.backend.AbstractBackend` :class:`~pepper.framework.abstract.application.AbstractApplication`
- Components & Intentions: :class:`~pepper.framework.abstract.component.AbstractComponent` :class:`~pepper.framework.abstract.intention.AbstractIntention`

Backend
=======

The framework.backend package contains the backends implementing Sensors, Actuators & Backend:

- :class:`~pepper.framework.backend.naoqi.backend.NAOqiBackend` implements the backend for Pepper & Nao Robots
- :class:`~pepper.framework.backend.system.backend.SystemBackend` implements the backend for Windows/Mac/Linux systems.

Sensor
======

The framework.sensor package implements Face, Object and Speech Recognition:

- :class:`~pepper.framework.sensor.api.VAD` implements Voice Activity Detection on Microphone input
- :class:`~pepper.framework.sensor.api.ASR` implements Automated Speech Recognition
- :class:`~pepper.framework.sensor.api.ObjectDetector` implements Object Detection
- :class:`~pepper.framework.sensor.api.FaceDetector` implements Face Detection
- :class:`~pepper.framework.sensor.api.Location` gets the current geographical location (WIP)

Component
=========

Applications are made out of several instances of :class:`~pepper.framework.abstract.component.AbstractComponent`,
which expose various methods and events to applications. They are summarized below:

- :class:`~pepper.framework.component.camera.CameraComponent` exposes the :meth:`~pepper.framework.component.camera.CameraComponent.on_image` event.
- :class:`~pepper.framework.component.speech_recognition.SpeechRecognitionComponent` exposes the :meth:`~pepper.framework.component.speech_recognition.SpeechRecognitionComponent.on_transcript` event.
- :class:`~pepper.framework.component.object_detection.ObjectDetectionComponent` exposes the :meth:`~pepper.framework.component.object_detection.ObjectDetectionComponent.on_object` event.
- :class:`~pepper.framework.component.face_detection.FaceRecognitionComponent` exposes the :meth:`~pepper.framework.component.face_detection.FaceRecognitionComponent.on_face`, :meth:`~pepper.framework.component.face_detection.FaceRecognitionComponentComponent.on_face_known` & :meth:`~pepper.framework.component.face_detection.FaceRecognitionComponent.on_face_new` events.
- :class:`~pepper.framework.component.text_to_speech.TextToSpeechComponent` exposes the :meth:`~pepper.framework.component.text_to_speech.TextToSpeechComponent.say` method.
- :class:`~pepper.framework.component.brain.BrainComponent` exposes :class:`pepper.brain.long_term_memory.LongTermMemory` to the application.

Some Components are more complex and require other components to work. They will raise a :class:`pepper.framework.abstract.component.ComponentDependencyError` if dependencies are not met.

- :class:`~pepper.framework.component.context.ContextComponent` exposes :class:`pepper.framework.context.Context` to the application and overrides the :meth:`~pepper.framework.component.context.ContextComponent.say` method to work with the :class:`~pepper.language.language.Chat` class. It also exposes the :meth:`~pepper.framework.component.context.ContextComponent.on_chat_turn`, :meth:`~pepper.framework.component.context.ContextComponent.on_chat_enter` & :meth:`~pepper.framework.component.context.ContextComponent.on_chat_exit` events.
- :class:`~pepper.framework.component.statistics.StatisticsComponent` displays realtime system statistics in the command line.
- :class:`~pepper.framework.component.scene.SceneComponent` creates a 3D scatterplot of the visible space.
- :class:`~pepper.framework.component.display.display.DisplayComponent` shows the live camera feedback and the 3D view of the current space, including the objects that are observed.

.. _pepper_tensorflow: https://github.com/cltl/pepper_tensorflow
"""
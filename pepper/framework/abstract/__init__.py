"""
Abstract
========

The framework.abstract package contains specifications for:

- Sensors: :class:`~pepper.framework.abstract.camera.AbstractCamera` :class:`~pepper.framework.abstract.microphone.AbstractMicrophone`
- Actuators: :class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech` :class:`~pepper.framework.abstract.motion.AbstractMotion` :class:`~pepper.framework.abstract.led.AbstractLed`
- Backends & Applications: :class:`~pepper.framework.abstract.backend.AbstractBackend` :class:`~pepper.framework.abstract.application.AbstractApplication`
- Components & Intentions: :class:`~pepper.framework.abstract.component.AbstractComponent` :class:`~pepper.framework.abstract.intention.AbstractIntention`

The :class:`~pepper.framework.abstract.application.AbstractApplication` class forms the base of each application,
which is built on top of an :class:`~pepper.framework.abstract.backend.AbstractBackend` instance.
Backends expose :class:`~pepper.framework.abstract.camera.AbstractCamera`,
:class:`~pepper.framework.abstract.microphone.AbstractMicrophone` and
:class:`~pepper.framework.abstract.text_to_speech.AbstractTextToSpeech` to the Application.

Applications can be extended by adding one or more :class:`~pepper.framework.abstract.component.AbstractComponent`.
More complex Applications can be build on several instances of
:class:`~pepper.framework.abstract.intention.AbstractIntention`, each of which deals with one task within an app.
"""

from .camera import AbstractCamera, AbstractImage
from .microphone import AbstractMicrophone
from .text_to_speech import AbstractTextToSpeech
from .motion import AbstractMotion
from .led import AbstractLed, Led
from .tablet import AbstractTablet

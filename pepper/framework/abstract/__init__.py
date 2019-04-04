"""
Contains Abstract Building Blocks for creating Robot Applications

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
from .led import AbstractLed, LeftEarLed, RightEarLed, LeftFaceLed, RightFaceLed

from .backend import AbstractBackend
from .component import AbstractComponent

from .application import AbstractApplication
from .intention import AbstractIntention

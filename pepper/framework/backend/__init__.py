"""
Backend
=======

The framework.backend package contains the backends implementing Sensors, Actuators & Backend:

- :class:`~pepper.framework.backend.naoqi.backend.NAOqiBackend` implements the backend for Pepper & Nao Robots
- :class:`~pepper.framework.backend.system.backend.SystemBackend` implements the backend for Windows/Mac/Linux systems.
"""

from .system import *

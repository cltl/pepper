"""
Framework for Creating Robot Applications
-----------------------------------------

- Abstract: Contains (Abstract) Specifications for Backend & Component, Camera, Microphone & Speech to Text
- Backend: Contains the Backends robot applications can run on
- Component: Contains the Components robot applications need
"""

from .abstract import *
from .component import *
from .sensor import *
from .context import Context
from .util import Bounds


from pepper.framework import AbstractComponent
from pepper.framework.abstract import AbstractComponent
from pepper.framework.component import ContextComponent
from pepper import logger

import numpy as np

from time import time
import random


class ExploreComponent(AbstractComponent):

    TIMEOUT = 15
    LAST_MOVE = 0
    SPEED = 0.05

    def __init__(self, backend):
        super(ExploreComponent, self).__init__(backend)

        log = logger.getChild(ExploreComponent.__name__)

        context = self.require(ExploreComponent, ContextComponent)  # type: ContextComponent

        def explore():

            # Get Observations, sorted (high to low) by last time seen
            observations = sorted(context.context.objects, key=lambda obj: obj.time)

            if observations and random.random() > 0.33333:

                # Look at least recently seen object
                log.debug("Look at {}".format(observations[0]))
                self.backend.motion.look(observations[0].direction, ExploreComponent.SPEED)
            else:

                # Look at random point
                log.debug("Look at random point")
                self.backend.motion.look((
                    float(np.clip(np.random.standard_normal() / 3 * np.pi/2, -np.pi, np.pi)),
                    float(np.clip(np.pi/2 + np.random.standard_normal() / 10 * np.pi, 0, np.pi))
                ), ExploreComponent.SPEED)

        def on_image(image):
            # At Every Tick
            if not context.context.chatting:
                if time() - ExploreComponent.LAST_MOVE > ExploreComponent.TIMEOUT:
                    explore()
                    ExploreComponent.LAST_MOVE = time()

        self.backend.camera.callbacks += [on_image]

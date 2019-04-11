from pepper.framework import AbstractComponent
from pepper.framework.component import ObjectDetectionComponent
from pepper import config

import numpy as np

from time import time
import random


class TrackComponent(AbstractComponent):
    def __init__(self, backend):
        super(TrackComponent, self).__init__(backend)

        if hasattr(backend, "session"):

            from naoqi import ALProxy

            # Tracking needs Object Detection, to Track "Person" Objects
            self._object_detection = self.require(TrackComponent, ObjectDetectionComponent)  # type: ObjectDetectionComponent

            self._video = ALProxy("ALVideoDevice", config.NAOQI_IP, config.NAOQI_PORT)
            self._motion = ALProxy("ALMotion", config.NAOQI_IP, config.NAOQI_PORT)
            self._motion.setStiffnesses("Head", 1.0)

            # Get Control over Robot Movement
            self._awareness = ALProxy("ALBasicAwareness", config.NAOQI_IP, config.NAOQI_PORT)
            self._awareness.setEngagementMode("FullyEngaged")
            self._awareness.setStimulusDetectionEnabled("People", False)
            self._awareness.setStimulusDetectionEnabled("Movement", False)
            self._awareness.setEnabled(True)

            self._last_person = time()

            def look(x, y, speed=1.25, speed_min=0.02, speed_max=0.3):
                phi, theta = self._video.getAngularPositionFromImagePosition(0, [x, y])

                speed_phi = max(1E-6, min(speed_max, speed * phi ** 2))
                speed_theta = max(1E-6, min(speed_max, speed * theta ** 2))

                if max(speed_phi, speed_theta) > speed_min:
                    self._motion.changeAngles("HeadYaw", phi, speed_phi)
                    self._motion.changeAngles("HeadPitch", theta, speed_theta)

            def random_look(speed=0.05):
                self._motion.setAngles("HeadYaw", random.uniform(-2.0857, 2.0857), speed)
                self._motion.setAngles("HeadPitch", random.uniform(-0.7068, 0.6371), speed)

            def on_image(image, orientation):
                if time() - self._last_person > 3:
                    random_look()

                    self._last_person = time()
                    self._awareness.setEnabled(True)

            def on_object(image, objects):
                # for obj in objects:
                #     if obj.name == 'bottle':
                #         # TODO: Get Object Angular Position, Move Into Dedicated Location
                #         phi, theta = self._video.getAngularPositionFromImagePosition(0, obj.bounds.center)
                #         phi += self._motion.getAngles("HeadYaw", False)[0]
                #         theta += self._motion.getAngles("HeadPitch", False)[0]
                #         print(phi, theta)

                people = [obj for obj in objects if obj.name == "person"]

                if people:
                    self._last_person = time()
                    self._awareness.setEnabled(False)

                    x = np.average([p.image_bounds.x0 + p.image_bounds.width / 2 for p in people],
                                   weights=[p.image_bounds.area for p in people])
                    y = np.average([p.image_bounds.y0 + p.image_bounds.height / 4 for p in people],
                                   weights=[p.image_bounds.area for p in people])

                    look(x, y)

            self.backend.camera.callbacks += [on_image]
            self._object_detection.on_object_callbacks += [on_object]

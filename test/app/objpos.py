from pepper.framework import *
from pepper import config

from time import time
import numpy as np


TIMEOUT = 10

class ObjPosApp(AbstractApplication, DisplayComponent, ContextComponent, SceneComponent,
                ObjectDetectionComponent, SpeechRecognitionComponent, FaceRecognitionComponent, TextToSpeechComponent):

    def __init__(self, backend):
        super(ObjPosApp, self).__init__(backend)

    ACTION = 0

    def on_face_known(self, faces):
        for face in faces:
            if face.name == "Bram":
                self.backend.motion.look(face.direction)

    # def on_object(self, objects):
    #
    #     observations =  sorted(self.context.objects, key=lambda obj: obj.time)
    #     print(["{} ({:0.2f})".format(obj, time() - obj.time) for obj in observations])
    #
    #     if observations:
    #         obj = observations[0]
    #
    #         if time() - self.ACTION > TIMEOUT:
    #             if time() - obj.time > 10:
    #                 print("Look at {}".format(obj))
    #                 self.ACTION = time()
    #                 self.backend.motion.point(obj.direction)
    #                 self.backend.motion.look(obj.direction)
    #
    #             else:
    #                 print("Look at random point")
    #
    #                 yaw = float(np.clip(np.random.standard_normal() / 3 * np.pi, -np.pi, np.pi))
    #                 pitch = float(np.clip(np.random.standard_normal() / 6 * np.pi, -np.pi/2, np.pi/2))
    #
    #                 self.backend.motion.point((yaw, pitch))
    #                 self.backend.motion.look((yaw, pitch))
    #                 self.ACTION = time()


if __name__ == '__main__':
    ObjPosApp(config.get_backend()).run()

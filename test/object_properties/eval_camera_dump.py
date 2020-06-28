"""
The script to generate evaluation data. Needs to be run within the Leolani framework.

Adapted from the camera_dump app written by Bram Kraaijeveld.
"""

import os

from datetime import datetime
from PIL import Image

from pepper.framework import *
from pepper import config


class EvalCameraDumpApp(AbstractApplication, ObjectDetectionComponent):

    OUTPUT_ROOT = os.path.join('./data', 'eval')

    def __init__(self, backend):
        super(EvalCameraDumpApp, self).__init__(backend)

        self.output = os.path.join(self.OUTPUT_ROOT, datetime.now().strftime("%Y%m%d_%H%M%S"))

    def on_object(self, objects):
        if objects:
            valid_objects = [obj for obj in objects if
                             obj.dict()['name'] != 'person' and obj.dict()['confidence'] > 0.5]
            if valid_objects:
                if not os.path.exists(self.output):
                    os.makedirs(self.output)
                image = valid_objects[0].image
                image.to_file(self.output)
                for vo in valid_objects:
                    if len([obj_dir for obj_dir in os.listdir(self.output) if os.path.isdir(obj_dir)]) > 100:
                        break
                    with open(os.path.join(self.output, "{}_obj.json".format(image.hash)), "w") as json_file:
                        json.dump([vo.dict() for vo in valid_objects], json_file)

                    hash = str(vo.id)

                    path = os.path.join(self.output, image.hash, hash)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    rgb = vo.image.get_image(vo.image_bounds)
                    meta = vo.dict()

                    Image.fromarray(rgb).save(os.path.join(path, "rgb.png"))
                    with open(os.path.join(path, "meta.json"), "w") as json_file:
                        json.dump(meta, json_file)

                self.log.info(objects)


if __name__ == '__main__':
    EvalCameraDumpApp(config.get_backend()).run()

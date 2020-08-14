import json
import os
from datetime import datetime

import numpy as np
from PIL import Image

from pepper.app_container import ApplicationContainer
from pepper.framework.abstract import AbstractApplication
from pepper.framework.component import ObjectDetectionComponent


class CameraDumpApp(ApplicationContainer, AbstractApplication, ObjectDetectionComponent):

    """

    """

    OUTPUT_ROOT = r"C:\Users\Pepper\Documents\Pepper\pepper\tmp\data"

    def __init__(self):
        super(CameraDumpApp, self).__init__()

        self.output = os.path.join(self.OUTPUT_ROOT, datetime.now().strftime("%Y%m%d_%H%M%S"))
        os.makedirs(self.output)

    def on_object(self, objects):
        if objects:

            # Save Image to Disk
            image = objects[0].image
            image.to_file(self.output)

            with open(os.path.join(self.output, "{}_obj.json".format(image.hash)), "w") as json_file:
                json.dump([obj.dict() for obj in objects], json_file)

            for obj in objects:

                hash = str(obj.id)

                path = os.path.join(self.output, image.hash, hash)
                os.makedirs(path)

                rgb = obj.image.get_image(obj.image_bounds)
                depth = obj.image.get_depth(obj.image_bounds)
                meta = obj.dict()

                Image.fromarray(rgb).save(os.path.join(path, "rgb.png"))
                np.save(os.path.join(path, "depth.npy"), depth)
                with open(os.path.join(path, "meta.json"), "w") as json_file:
                    json.dump(meta, json_file)

            self.log.info(objects)


if __name__ == '__main__':
    CameraDumpApp().run()

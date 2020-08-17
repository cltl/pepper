from PIL import Image
import numpy as np

import json
import os

from pepper.framework.abstract import AbstractImage
from pepper.framework.sensor.api import Object
from pepper.framework.util import Bounds


def read(root):

    OBJ_HANDLE = "_obj.json"
    RGB_HANDLE = "_rgb.png"
    DEPTH_HANDLE = "_depth.npy"
    META_HANDLE = "_meta.json"

    obj_files = sorted([item for item in os.listdir(root) if item.endswith(OBJ_HANDLE)])

    for obj_file in obj_files:
        hash = obj_file.replace(OBJ_HANDLE, "")

        with open(os.path.join(root, hash + OBJ_HANDLE)) as obj_file:
            objs = json.load(obj_file)
        with open(os.path.join(root, hash + META_HANDLE)) as meta_file:
            meta = json.load(meta_file)

        rgb = np.array(Image.open(os.path.join(root, hash + RGB_HANDLE)))
        depth = np.load(os.path.join(root, hash + DEPTH_HANDLE))

        img = AbstractImage(rgb, Bounds.from_json(meta["bounds"]), depth, meta["time"])

        # TODO: Is this always the correct image for the objects?
        objects = [Object.from_json(obj, img) for obj in objs]

        yield img, objects


if __name__ == '__main__':

    for image, objects in read(r"C:\Users\Pepper\Documents\Pepper\pepper\tmp\data\20190930_125844"):

        print(image.time, image, objects)

        for obj in objects:
            print(obj.image_bounds, image.get_image(obj.image_bounds).shape)


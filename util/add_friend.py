from __future__ import print_function

from pepper.framework.sensor.face import OpenFace
from pepper import config

from scipy.ndimage import imread
from scipy.misc import imresize
import numpy as np

import os


def add_friend_from_directory(directory, name, max_size=1024):

    openface = OpenFace()
    vectors = []

    listdir = os.listdir(directory)

    for i, item in enumerate(listdir, 1):

        print("\rDetecting Face {}/{}".format(i, len(listdir)), end="")

        # Try Loading Image, Resizing if necessary
        try: image = imread(os.path.join(directory, item))
        except: continue

        image_size = max(image.shape[0], image.shape[1])
        if image_size > max_size:
            image = imresize(image, max_size/float(image_size))

        # Represent Face as a 128-bit vector
        representation = openface.represent(image)
        if representation:
            face, bounds = representation[0]
            vectors.append(face)

    # Write Data to .bin file
    with open(os.path.join(config.PEOPLE_FRIENDS_ROOT, "{}.bin".format(name)), 'wb') as bin:
        bin.write(np.concatenate(vectors))


if __name__ == '__main__':
    pass

    # Use:
    # add_friend_from_directory('<directory>', '<name>')
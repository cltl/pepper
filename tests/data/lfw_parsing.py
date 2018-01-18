from pepper.vision.classification.face import FaceRecognition
from scipy.misc import imread
import numpy as np
import os


ROOT = r"C:\Users\Bram\Documents\Pepper\data\lfw"

recognition = FaceRecognition()
with open('lfw/matrix.bin', 'wb') as matrix, open('lfw/names.txt', 'wb') as names:
    for person in os.listdir(ROOT):
        person_path = os.path.join(ROOT, person)

        for photo in os.listdir(person_path):
            print("{:30s}{}".format(person, photo))

            image = imread(os.path.join(person_path, photo))
            result = recognition.representation(image)

            if result:
                bounds, representation = result
                names.write(person.encode('utf-8') + "\r\n")
                matrix.write(representation)

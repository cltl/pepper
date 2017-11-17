from PIL import Image
from pepper.vision.classification.faces import Faces
import os
import numpy as np
import yaml


DIR = r"C:\Users\Bram\Documents\Pepper\data\lfw"

faces = Faces()


with open("lfw_names.txt", 'w') as lfw_names, open("lfw_vector.bin", 'wb') as lfw_vector:
    for person in os.listdir(DIR):
        print(person)

        representation = []

        for image in os.listdir(os.path.join(DIR, person)):
            people = faces.represent(Image.open(os.path.join(DIR, person, image)))
            if people: representation.append(people[0][1])
            print("\t{}".format(image))

        if representation:
            lfw_names.write("{};".format(person))
            lfw_vector.write(np.mean(np.array(representation, np.float32), 0).tobytes())

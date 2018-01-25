from pepper.vision.classification.face import FaceRecognition

from scipy.io import loadmat
from scipy.misc import imread
import numpy as np
import matplotlib.pyplot as plt

import datetime
import os


MAT_PATH = r"C:\Users\Bram\Documents\Pepper\data\people\wiki\wiki.mat"
ROOT = r"C:\Users\Bram\Documents\Pepper\data\people\wiki"

D0 = datetime.datetime(1, 1, 1)

_dob, _taken, _path, _gender, _name, _crop, _score, _score2 = loadmat(MAT_PATH)['wiki'][0][0]

TOTAL = 0

recognition = FaceRecognition()
with open('wiki_matrix.bin', 'wb') as matrix, open('wiki_gender_age.bin', 'wb') as wiki_gender_age, open('wiki_names.txt', 'wb') as wiki_names:
    for i, (dob, taken, gender, name, path, crop, score) in enumerate(zip(_dob[0], _taken[0], _gender[0], _name[0], _path[0], _crop[0], _score[0])):

        if not np.isinf(score):
            try:
                dob = (D0 + datetime.timedelta(dob))
                taken = datetime.datetime(taken, 6, 1)

                age = D0 + (taken - dob) if taken > dob else D0
                age = age.year + age.month / 12.0

                name = name[0] if name else u''
                path = path[0]
                gender = None if np.isnan(gender) else bool(gender)

                # print(dob.year, taken.year, age, gender, name, path, score, crop)

                image = imread(os.path.join(ROOT, path))

                if len(image.shape) >= 2:
                    if len(image.shape) == 2:
                        image = image.reshape(image.shape[0], image.shape[1], 1)

                    result = recognition.representation(image)

                    if result and not gender is None:
                        bounds, representation = result

                        matrix.write(representation)

                        wiki_gender_age.write(np.array(gender, np.bool))
                        wiki_gender_age.write(np.array(age, np.float32))

                        wiki_names.write(name.encode('utf-8') + "\r\n")

                        TOTAL += 1

                    print "\r{}/{}: {:3.1%} - {}".format(i, len(_dob[0]), i / float(len(_dob[0])), TOTAL),
            except Exception as e:
                print(e)
                print("index: {}".format(i))

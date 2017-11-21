import os
import numpy as np

LFW_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'lfw_names.txt')
LFW_VECTOR_PATH = os.path.join(os.path.dirname(__file__), 'lfw_matrix.bin')

FACE_NAMES_PATH = os.path.join(os.path.dirname(__file__), 'face_names.txt')
FACE_VECTOR_PATH = os.path.join(os.path.dirname(__file__), 'face_matrix.bin')


def load_lfw():
    with open(LFW_NAMES_PATH) as lfw_names_file:
        lfw_names = lfw_names_file.read().split(';')

    lfw_vector = np.fromfile(LFW_VECTOR_PATH, np.float32).reshape(len(lfw_names), 128)

    return lfw_names, lfw_vector


def load_faces():
    with open(FACE_NAMES_PATH) as face_names_file:
        names = face_names_file.read().split(';')

    vector = np.fromfile(FACE_VECTOR_PATH, np.float32).reshape(len(names), 128)
    return names, vector


def save_faces(names, vector):
    assert vector.shape == (len(names), 128)

    with open(FACE_NAMES_PATH, 'w') as face_names_file:
        face_names_file.write(';'.join(names))

    with open(FACE_VECTOR_PATH, 'wb') as face_vector_file:
        face_vector_file.write(vector)
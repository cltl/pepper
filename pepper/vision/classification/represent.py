import openface
import cv2
import sys
import os
import json

MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
DLIB_DIR = os.path.join(MODEL_DIR, 'dlib')
OPENFACE_DIR = os.path.join(MODEL_DIR, 'openface')
DIM = 96

IMAGE_PATH = sys.argv[1]
image = cv2.cvtColor(cv2.imread(IMAGE_PATH), cv2.COLOR_BGR2RGB)

align = openface.AlignDlib(os.path.join(DLIB_DIR, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(OPENFACE_DIR, "nn4.small2.v1.t7"), DIM)

bounding_box = align.getLargestFaceBoundingBox(image)
aligned_face = align.align(DIM, image, bounding_box, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
representation = net.forward(aligned_face)

print json.dumps(representation.tolist())
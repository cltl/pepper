# This Script gets Executed inside the 'bamos/openface' Docker Container #

import openface
import numpy as np

import os
import socket


MODEL_DIR = os.path.join(os.path.dirname(__file__), 'models')
DLIB_DIR = os.path.join(MODEL_DIR, 'dlib')
OPENFACE_DIR = os.path.join(MODEL_DIR, 'openface')
DIM = 96

ADDRESS = ('', 8989)

align = openface.AlignDlib(os.path.join(DLIB_DIR, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(OPENFACE_DIR, "nn4.small2.v1.t7"), DIM)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDRESS)

try:
    while True:
        server.listen(5)
        connection, address = server.accept()
        print(connection, address)
        shape = np.frombuffer(connection.recv(3*4), np.int32)
        length = np.prod(shape)

        print(shape)
        print(length)

        data = bytearray()
        while len(data) < length:
            data.extend(connection.recv(1024*4))

        image = np.frombuffer(data, np.uint8).reshape(shape)

        bounding_boxes = align.getAllFaceBoundingBoxes(image)

        connection.sendall(np.int32(len(bounding_boxes)))

        for i in range(len(bounding_boxes)):
            bounding_box = bounding_boxes[i]

            bounds = np.array([[bounding_box.left(), bounding_box.top()],
                               [bounding_box.width(), bounding_box.height()]],
                              np.float32)

            bounds /= image.shape[:2]

            connection.sendall(bounds)

            aligned_face = align.align(DIM, image, bounding_box,
                                       landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
            representation = net.forward(aligned_face)

            connection.sendall(np.int32(len(representation)))
            connection.sendall(representation.astype(np.float32))

finally:
    server.close()
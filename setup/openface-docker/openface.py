# This Script gets Executed inside the 'bamos/openface' Docker Container #

import openface  # The Openface package is imported inside the Docker Container
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
    server.listen(1)
    print("Started server at " + str(server.getsockname()))
    while True:
        connection, address = server.accept()

        try:
            shape = np.frombuffer(connection.recv(3*4), np.int32)
            length = np.prod(shape)

            image = np.empty(shape, np.uint8)
            connection.recv_into(image, length, socket.MSG_WAITALL)

            bounding_boxes = align.getAllFaceBoundingBoxes(image)

            if bounding_boxes:
                connection.sendall(np.int32(len(bounding_boxes)))

                for bounding_box in bounding_boxes:
                    bounds = np.array([[bounding_box.left() , bounding_box.top()],
                                       [bounding_box.right(), bounding_box.bottom()]],
                                      np.float32)

                    connection.sendall(bounds)

                    aligned_face = align.align(DIM, image, bounding_box,
                                               landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
                    representation = net.forward(aligned_face)
                    connection.sendall(representation.astype(np.float32))
                print("Found {} face(s)".format(len(bounding_boxes)))
            else:
                connection.sendall(np.int32(0))

        except Exception as e:
            print("Failed to process image: " + str(e))
        finally:
            connection.close()

finally:
    server.close()
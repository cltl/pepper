from PIL import Image
import numpy as np
import json

from io import BytesIO
import socket


class ObjectClassifyClient:
    def __init__(self, address = ('localhost', 9999)):
        """
        Classify Images using Inception Model

        Parameters
        ----------
        address: (str, int)
            Address of Inception Model Host
        """
        self.address = address

    def classify(self, image):
        """
        Parameters
        ----------
        image: np.ndarray

        Returns
        -------
        classification: list of (float, list)
            List of confidence-object pairs, where object is a list of object synonyms
        """

        jpeg = self._convert_to_jpeg(image)
        jpeg_size = np.array([len(jpeg)], np.uint32)

        s = socket.socket()
        s.connect(self.address)
        s.sendall(jpeg_size)
        s.sendall(jpeg)
        response = json.loads(s.recv(4096).decode())
        return response

    def _convert_to_jpeg(self, image):
        """
        Parameters
        ----------
        image: np.ndarray

        Returns
        -------
        encoded_image: bytes
        """

        with BytesIO() as jpeg_buffer:
            Image.fromarray(image).save(jpeg_buffer, format='JPEG')
            return jpeg_buffer.getvalue()


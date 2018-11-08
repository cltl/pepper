from pepper.sensor import CocoClassifyClient, OpenFace, FaceClassifier
from pepper import config

from PIL import Image, ImageDraw, ImageFont
import colorsys
import numpy as np

import time
import os


class ImageWriter(object):
    def __init__(self, path=os.path.join(config.PROJECT_ROOT, 'imglog'), extension=".jpeg"):
        """
        Utility to Write Images to File

        Parameters
        ----------
        path: str
            Root directory for images
        extension: str
            Image file type
        """
        self._path = os.path.join(path, time.strftime("%y%m%d-%H%M%S"))
        self._extension = extension
        self._index = 0

        if not os.path.exists(self._path): os.makedirs(self._path)

    @property
    def path(self):
        return self._path

    @property
    def extension(self):
        return self._extension

    def write(self, image):
        Image.fromarray(image).save_person(os.path.join(self._path, "{:05d}{}".format(self._index, self.extension)))
        self._index += 1


class ImageAnnotator(object):
    def __init__(self):
        """
        Annotate Images with CoCo & OpenFace Bounding Boxes

        Parameters
        ----------
        path: str
            Folder with stored faces
        """

        self._font_size = 12
        self._font_name = "Montserrat-Regular.ttf"
        self._font = ImageFont.truetype(os.path.join(os.path.dirname(__file__), self._font_name), self._font_size)

    def annotate_batch(self, directory, output_directory=None, extension='.png',
                       object_threshold=config.OBJECT_RECOGNITION_THRESHOLD,
                       face_threshold=config.FACE_RECOGNITION_THRESHOLD):

        if not output_directory:
            output_directory = os.path.join(directory, 'annotated')
        if not os.path.exists(output_directory): os.makedirs(output_directory)

        image_paths = [path for path in os.listdir(directory) if os.path.isfile(os.path.join(directory, path))]

        coco = CocoClassifyClient()
        openface = OpenFace()
        face_classifier = FaceClassifier.from_directory(config.PEOPLE_FRIENDS_ROOT)

        for index, image_path in enumerate(image_paths):
            print "\rAnnotating Image {:d}/{:d}".format(index + 1, len(image_paths)),
            image = Image.open(os.path.join(directory, image_path))
            image_np = np.array(image)

            objects = coco.classify(image_np)
            persons = [face_classifier.classify(face) for face in openface.represent(image_np)]

            image = self.annotate(image, objects, persons, object_threshold, face_threshold)
            image.save(os.path.join(output_directory, image_path.replace(os.path.splitext(image_path)[1], extension)))

        print("\n")

    def annotate(self, image, objects, persons,
                 object_threshold=config.OBJECT_RECOGNITION_THRESHOLD,
                 face_threshold=config.FACE_RECOGNITION_THRESHOLD):
        """
        Annotate Image

        Parameters
        ----------
        image: Image.Image
            Input Image
        objects: list of pepper.sensor.obj.CocoObject
        faces: list of pepper.sensor.face.Face
        persons: list of pepper.sensor.face.Person
        object_threshold: float
            Confidence Threshold for Object Recognition Annotations
        face_threshold: float
            Confidence Threshold for Face Recognition Annotations

        Returns
        -------
        image: Image.Image
            Annotated Image
        """

        draw = ImageDraw.Draw(image)

        # Annotate Objects
        for obj in objects:

            if obj.confidence > object_threshold:

                color = colorsys.hsv_to_rgb(float(obj.id - 1) / CocoClassifyClient.CLASSES, 1, 1)
                color = tuple((np.array(color) * 255).astype(np.uint8))

                bounds = obj.bounds.scaled(image.width, image.height)

                self._draw_bounds(draw, bounds, color, 3)
                self._draw_text(draw, bounds, "[{:4.0%}] {}".format(obj.confidence, obj.name), color, (0, 0, 0))

        # Annotate Persons
        for person in persons:
            text = "[{:4.0%}] {}".format(person.confidence, person.name if person.confidence > face_threshold else "human")
            bounds = person.bounds.scaled(image.width, image.height)

            color = (255, 255, 255)

            self._draw_bounds(draw, bounds, color, 3)
            self._draw_text(draw, bounds, text, color, (0, 0, 0))

        return image

    @staticmethod
    def _draw_bounds(draw, bounds, fill, width):
        """
        Parameters
        ----------
        draw: ImageDraw.ImageDraw
            ImageDraw Object
        bounds: pepper.sensor.obj.Bounds
            [x0, y0, x1, y1]
        """

        draw.line([bounds.x0, bounds.y0, bounds.x0, bounds.y1], fill, width)
        draw.line([bounds.x0, bounds.y0, bounds.x1, bounds.y0], fill, width)
        draw.line([bounds.x1, bounds.y1, bounds.x0, bounds.y1], fill, width)
        draw.line([bounds.x1, bounds.y1, bounds.x1, bounds.y0], fill, width)

    def _draw_text(self, draw, bounds, text, fill, color):
        """
        Parameters
        ----------
        draw: ImageDraw.ImageDraw
            ImageDraw Object
        bounds: pepper.sensor.obj.Bounds
        text: str
        """
        draw.rectangle([bounds.x0, bounds.y1 - self._font_size, bounds.x1, bounds.y1], fill)
        draw.text([bounds.x0 + 5, bounds.y1 - self._font_size], text, color, self._font)


if __name__ == '__main__':
    ImageAnnotator().annotate_batch("/Users/bram/Documents/pepper/pepper/imglog/181004-120211")

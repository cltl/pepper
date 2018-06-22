import matplotlib
matplotlib.use('Qt5Agg')
matplotlib.rcParams['toolbar'] = 'None'
import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import cm

import pepper
import numpy as np

from threading import Thread
from queue import Queue, Empty
from random import choice
from time import sleep, time


def enumerate_objects(dictionary):
    string = ""
    for cls, count in dictionary.items():
        string += "{} {}".format(count, cls) + ("s, " if count > 1 else ", ")
    object_string = string[:-2]

    if ', ' in object_string:
        k = object_string.rfind(',')
        string = object_string[:k] + ' and' + object_string[k + 1:]

    return string

class ObjectRecognitionApp(pepper.App):

    GREET = ["Hello", "Hi", "Hey there", "Greetings", "Good day", "Nice to see you", "It's a pleasure", "Hey"]

    RESOLUTION = pepper.CameraResolution.VGA_640x480
    SCORE_THRESHOLD = 0.5
    FACE_THRESHOLD = 0.8
    MAX_BOXES = 4
    FACE_BB_WIDEN = 8

    FACE_TIMEOUT = 60

    LABEL_HEIGHT = 20

    FONT = {
        'family': 'sans',
        'color':  'black',
        'weight': 'normal',
        'size': 16,
    }

    FACE_FONT = {
        'family': 'sans',
        'color': 'white',
        'weight': 'normal',
        'size': 14,
    }

    def __init__(self):
        super(ObjectRecognitionApp, self).__init__(pepper.ADDRESS)

        self.text_to_speech = self.session.service("ALAnimatedSpeech")

        self.camera = pepper.PepperCamera(self.session, resolution=self.RESOLUTION)
        self.coco = pepper.CocoClassifyClient()

        self.openface = pepper.OpenFace()
        self.people_classifier = pepper.PeopleClassifier.from_directory(pepper.PeopleClassifier.LEOLANI)

        self.last_name = ""
        self.last_name_time = 0
        self.face_queue = Queue()
        self.last_objects = {}
        self.all_objects = {}

        Thread(target=self.reaction_worker).start()

        # Plotting
        self.figure, self.axis = plt.subplots()
        self.axis.set_xticks([])
        self.axis.set_yticks([])
        self.axis.set_xlim(0, 640)
        self.axis.set_ylim(0, 480)
        plt.gca().invert_yaxis()

        self.plot = self.axis.imshow(self.camera.get())

        self.colors = [cm.hsv(x) for x in np.linspace(0, 1, 91)]

        self.rectangles = [patches.Rectangle((0, 0), 0, 0, linewidth=2, fill=False) for i in range(self.MAX_BOXES)]
        [self.axis.add_patch(rectangle) for rectangle in self.rectangles]

        self.label_rectangles = [patches.Rectangle((0, 0), 0, 0) for i in range(self.MAX_BOXES)]
        [self.axis.add_patch(rectangle) for rectangle in self.label_rectangles]
        self.labels = [self.axis.text(0, 0, "", fontdict=self.FONT, va='center') for i in range(self.MAX_BOXES)]

        self.face_rectangle = patches.Rectangle((0, 0), 0, 0, linewidth=2, fill=False)
        self.face_rectangle.set_zorder(2000)
        self.face_label_rectangle = patches.Rectangle((0, 0), 0, 0)
        self.face_label_rectangle.set_zorder(2000)
        self.face_label = self.axis.text(0, 0, "", fontdict=self.FACE_FONT, va='center')
        self.face_label.set_zorder(2001)

        self.axis.add_patch(self.face_rectangle)
        self.axis.add_patch(self.face_label_rectangle)

        plt.tight_layout()
        plt.show(False)

        self.on_update()

    def say(self, text, speed=80):
        self.log.info(u"Leolani: '{}'".format(text))
        self.text_to_speech.say(ur"\\rspd={}\\{}".format(speed, text))

    def reaction_worker(self):
        while True:
            # React to Peoples Faces
            try:
                name, confidence, distance = self.face_queue.get(False)
                if name != self.last_name or time() - self.last_name_time > self.FACE_TIMEOUT:

                    self.say("{}, {}!".format(choice(self.GREET), name))
                    self.last_name = name
                    self.last_name_time = time()

                    if self.last_objects:
                        self.say("I see " + enumerate_objects(self.last_objects) + ".")

                    if self.all_objects:
                        self.say("Since I was looking, I have seen " + enumerate_objects(self.all_objects) + ".")

            except Empty:
                pass

            sleep(1)

    def on_image(self, image):
        self.plot.set_data(image)

        height, width, channels = image.shape
        classes, scores, boxes = self.coco.classify(image)

        # Update Last Objects
        self.last_objects = {}

        for cls, scr, box in zip([cls['name'] for cls in classes], scores, boxes):
            if scr > self.SCORE_THRESHOLD:
                if not cls in self.last_objects:
                    self.last_objects[cls] = 1
                else:
                    self.last_objects[cls] += 1

        for cls, count in self.last_objects.items():
            if not cls in self.all_objects:
                self.all_objects[cls] = count
            elif self.all_objects[cls] < count:
                self.all_objects[cls] = count

        face = self.openface.represent(image)
        if face:
            bounds, representation = face
            name, confidence, distance = self.people_classifier.classify(representation)

            if confidence > self.FACE_THRESHOLD:
                self.face_queue.put((name, confidence, distance))
            # else:
            #     self.face_queue.put(("Human", confidence, distance))

            x = bounds.x - self.FACE_BB_WIDEN
            y = bounds.y - self.FACE_BB_WIDEN
            w = bounds.width + 2 * self.FACE_BB_WIDEN
            h = bounds.height + 2 * self.FACE_BB_WIDEN

            self.face_rectangle.set_bounds(x, y, w, h)
            self.face_label_rectangle.set_color('black')

            self.face_label_rectangle.set_bounds(x, y+h, w, self.LABEL_HEIGHT)
            self.face_label_rectangle.set_color('black')

            self.face_label.set_x(x+5)
            self.face_label.set_y(y+h + self.LABEL_HEIGHT/2)

            if confidence > self.FACE_THRESHOLD:
                self.face_label.set_text("{} ({:3.0%})".format(name, confidence))
            else:
                self.face_label.set_text("unknown")
        else:
            self.face_rectangle.set_bounds(0, 0, 0, 0)
            self.face_label_rectangle.set_bounds(0, 0, 0, 0)
            self.face_label.set_text("")

        for rct, label_rct, label, cls, score, box in zip(
                self.rectangles, self.label_rectangles, self.labels, classes, scores, boxes):

            if score > self.SCORE_THRESHOLD:
                x = box[1] * width
                y = box[0] * height
                w = (box[3]-box[1]) * width
                h = (box[2]-box[0]) * height

                rct.set_bounds(x, y, w, h)
                rct.set_color(self.colors[cls['id']])
                rct.set_zorder(1000-y)

                label_rct.set_bounds(x, y+h-self.LABEL_HEIGHT, w, self.LABEL_HEIGHT)
                label_rct.set_color(self.colors[cls['id']])
                label_rct.set_zorder(1000-y)

                label.set_x(x+5)
                label.set_y(y+h-self.LABEL_HEIGHT/2)
                label.set_text("{} ({:3.0%})".format(cls['name'], score))
                label.set_zorder(1001-y)
            else:
                rct.set_bounds(0, 0, 0, 0)
                label_rct.set_bounds(0, 0, 0, 0)
                label.set_text("")

        self.figure.canvas.draw()
        self.figure.canvas.flush_events()


    def on_update(self):
        while True:
            self.on_image(self.camera.get())


if __name__ == "__main__":
    ObjectRecognitionApp()
from pepper.framework.system import SystemCamera
from pepper.framework import CameraResolution
from pepper.sensor.obj import CocoClassifyClient

import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import cm
import numpy as np

from Queue import Queue


MAX_BOXES = 4
LABEL_HEIGHT = 20
SCORE_THRESHOLD = 0.5

FONT = {
    'family': 'sans',
    'color': 'black',
    'weight': 'normal',
    'size': 16,
}

queue = Queue(maxsize=1)

camera = SystemCamera(CameraResolution.QVGA, 1, [lambda image: not queue.qsize() and queue.put(image)])
coco = CocoClassifyClient()

figure, axis = plt.subplots()
axis.set_xticks([])
axis.set_yticks([])
axis.set_xlim(0, camera.width)
axis.set_ylim(0, camera.height)
plt.gca().invert_yaxis()

plot = axis.imshow(np.empty((camera.height, camera.width, 3)))


# All Kinds of Rectangles
rectangles = [patches.Rectangle((0, 0), 0, 0, linewidth=2, fill=False) for i in range(MAX_BOXES)]
[axis.add_patch(rectangle) for rectangle in rectangles]
label_rectangles = [patches.Rectangle((0, 0), 0, 0) for i in range(MAX_BOXES)]
[axis.add_patch(rectangle) for rectangle in label_rectangles]
labels = [axis.text(0, 0, "", fontdict=FONT, va='center') for i in range(MAX_BOXES)]

colors = [cm.hsv(x) for x in np.linspace(0, 1, 600)]

plt.show(False)

camera.start()


while True:
    image = queue.get()

    plot.set_data(image)

    height, width, channels = image.shape
    classes, scores, boxes = coco.classify(image)


    for rct, label_rct, label, cls, score, box in zip(
            rectangles, label_rectangles, labels, classes, scores, boxes):

        if score > SCORE_THRESHOLD:
            x = box[1] * width
            y = box[0] * height
            w = (box[3] - box[1]) * width
            h = (box[2] - box[0]) * height

            rct.set_bounds(x, y, w, h)
            rct.set_color(colors[cls['id']])
            rct.set_zorder(1000 - y)

            label_rct.set_bounds(x, y + h - LABEL_HEIGHT, w, LABEL_HEIGHT)
            label_rct.set_color(colors[cls['id']])
            label_rct.set_zorder(1000 - y)

            label.set_x(x + 5)
            label.set_y(y + h - LABEL_HEIGHT / 2)
            label.set_text("{} ({:3.0%})".format(cls['name'], score))
            label.set_zorder(1001 - y)
        else:
            rct.set_bounds(0, 0, 0, 0)
            label_rct.set_bounds(0, 0, 0, 0)
            label.set_text("")

    figure.canvas.draw()
    figure.canvas.flush_events()

    # Close when plot window is closed
    if not plt.fignum_exists(1):
        exit()



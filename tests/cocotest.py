import pepper

from pepper.visualisation.coco import *
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt



class CocoTest(pepper.App):
    def __init__(self):
        super(CocoTest, self).__init__(pepper.ADDRESS)

        self.camera = pepper.PepperCamera(self.session)
        self.coco = pepper.CocoClassifyClient()

        self.figure, self.axis = plt.subplots()
        self.image = self.axis.imshow(self.camera.get())
        self.animation = FuncAnimation(self.figure, self.update, interval=0)
        plt.show()


    def update(self, i):
        image = self.camera.get()
        classes, scores, boxes = self.coco.classify(image)

        boxes = np.array(boxes)

        index = {cls['id']: {'name': cls['name']} for cls in classes}

        visualize_boxes_and_labels_on_image_array(
            image, boxes, [cls['id'] for cls in classes], scores, index,
            use_normalized_coordinates=True)
        self.image.set_data(image)


if __name__ == "__main__":
    CocoTest().run()
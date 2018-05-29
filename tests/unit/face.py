import pepper
from threading import Thread


class FaceRecognitionApp(pepper.App):
    def __init__(self):
        super(FaceRecognitionApp, self).__init__(pepper.ADDRESS)

        self._camera = pepper.PepperCamera(self.session)
        self._camera_thread = Thread(target=self._update_camera)

        self._open_face = pepper.OpenFace()
        self._people = pepper.PeopleClassifier.load_directory(pepper.PeopleClassifier.LEOLANI)
        self._people_classifier = pepper.PeopleClassifier(self._people)

        self._camera_thread.start()

        print("Booted")

    def on_camera(self, image):
        face = self._open_face.represent(image)
        if face: self.on_face(*face)

    def on_face(self, bounds, representation):
        name, confidence, distance = self._people_classifier.classify(representation)

        print(name, confidence, distance)

    def _update_camera(self):
        while True:
            self.on_camera(self._camera.get())


if __name__ == "__main__":
    FaceRecognitionApp().run()
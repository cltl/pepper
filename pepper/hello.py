from pepper.image.classify import ClassifyClient
from experiments.image import Resolution, ColorSpace

import qi, time, sys, random
from PIL import Image


GREETINGS = [
    "Hi",
    "Hello",
    "How are you?",
    "How are you doing?",
    "Hello there",
    "What's up",
    "Yo!",
    "Long time no see"
]

RECOGNISE = [
    "Eehhrm, I have no clue at all, but the word {} comes into my mind.."
    "It's quite unlikely, but is that a {}?",
    "I don't know for sure, but does that happen to be a {}?",
    "I see a {}!",
    "That is a {}!",
    "Yes, a {}! I know for sure!"
]


class HelloFace(object):
    def __init__(self, app):
        app.start()

        self.session = app.session

        self.face_time = 0
        self.face_count = 0

        self.TMP = r'C:\Users\Bram\Documents\Pepper\pepper\tmp\capture.jpg'
        self.client = ClassifyClient(('localhost', 9999))

        self.animated_speech = self.session.service("ALAnimatedSpeech")

        self.memory = self.session.service("ALMemory")

        self.video_service_id = "HelloObject1"
        self.video_service = self.session.service("ALVideoDevice")
        self.video_client = self.video_service.subscribe(self.video_service_id, int(Resolution.VGA), int(ColorSpace.RGB), 5)

        self.face_subscriber = self.memory.subscriber("FaceDetected")
        self.face_subscriber.signal.connect(self.on_face)

        self.face_detection_id = "HelloFace"
        self.face_detection = self.session.service("ALFaceDetection")
        self.face_detection.subscribe(self.face_detection_id)

    def on_face(self, value):
        if value:
            timestamp = value[0]
            faces = value[1][:-1]

            if len(faces) > self.face_count and time.time() - self.face_time > 15:
                self.face_count = len(faces)
                self.face_time = time.time()

                width, height, layers, color_space, seconds, milliseconds, data, camera_id, \
                angle_left, angle_top, angle_right, angle_bottom = self.video_service.getImageRemote(self.video_client)

                greeting = random.choice(GREETINGS)
                self.animated_speech.say(greeting)
                print("Detected {} face(s) @ {} -> {}".format(len(faces), time.strftime("%H:%M:%S"), greeting))

                Image.frombytes("RGB", (width, height), str(data)).save(self.TMP)
                predictions = self.client.classify(self.TMP)

                probability, labels = predictions[0]

                print("{:3.2%} -> {}".format(probability, labels))

                for i, sentence in enumerate(RECOGNISE):
                    if probability < i / float(len(RECOGNISE)):
                        self.animated_speech.say(sentence.format(random.choice(labels)))
                        break
                else:
                    self.animated_speech.say(RECOGNISE[-1].format(random.choice(labels)))

        else:
            self.face_count = 0

    def run(self):
        print("Starting Program")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)

    def __del__(self):
        self.face_detection.unsubscribe(self.face_detection_id)
        self.video_service.unsubscribe(self.video_service_id)


if __name__ == "__main__":
    ADDRESS = "192.168.1.100", 9559

    try:
        url = "tcp://{}:{}".format(*ADDRESS)
        app = qi.Application(["AName", "--qi-url={}".format(url)])
        hello_face = HelloFace(app)
        hello_face.run()

    except RuntimeError as e:
        print("Error while Connecting: {}".format(e))
        sys.exit(1)

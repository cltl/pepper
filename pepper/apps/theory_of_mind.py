import pepper

from pepper.language.analyze_utterance import analyze_utterance

from threading import Thread
from time import sleep
from random import choice


LAST_RESORT = [
    "I see",
    "Interesting",
    "Good to know",
    "I do not know, but I have a joke {insert joke}",
    "As the prophecy foretold",
    "But at what cost?",
    "So let it be written, ... so let it be done",
    "So ... it   has come to this",
    "That's just what he/she/they would've said",
    "Is this why fate brought us together?",
    "And thus, I die",
    "... just like in my dream",
    "Be that as it may, still may it be as it may be",
    "There is no escape from destiny",
    "Wise words by wise men write wise deeds in wise pen",
    "In this economy?",
    "and then the wolves came",
    "Many of us feel that way"
]


class TheoryOfMindApp(pepper.App):

    # Camera Resolution and Frequency, to tune performance!
    CAMERA_RESOLUTION = pepper.CameraResolution.VGA_320x240
    CAMERA_FREQUENCY = 1

    PERSON_RECOGNITION_THRESHOLD = 0.25
    NEW_PERSON_THRESHOLD = 0.01

    TEXT_TO_SPEECH_SPEED = 90

    def __init__(self, address):
        """
        Connect and Initialize Theory of Mind Application

        Parameters
        ----------
        address (<ip>, <port>)
        """
        super(TheoryOfMindApp, self).__init__(address)

        # Speech to Text and Text to Speech
        self.tts = self.session.service("ALAnimatedSpeech")
        self.asr = pepper.GoogleASR('en-GB')
        self.name_asr = pepper.NameASR()

        # Pepper's Ears
        self.microphone = pepper.PepperMicrophone(self.session)
        self.utterance = pepper.Utterance(self.microphone, self.on_utterance)

        # Pepper's Eyes
        self.camera = pepper.PepperCamera(self.session, resolution=self.CAMERA_RESOLUTION)
        self.openface = pepper.OpenFace()  # Docker must running and 'bamos/openface' image has to be pulled

        # Pepper's Friends
        self.people = pepper.load_people()
        self.cluster = pepper.PeopleCluster(self.people)

        # Last seen person by Pepper, Speech get's attributed to this person.
        self.current_person = None
        self.current_person_confidence = 0

        ## Start Systems ##
        Thread(target=self.update).start()  # Start Looking for Faces
        self.utterance.start()  # Start Listening for Speech

        self.log.info("Application Started")

    def on_utterance(self, audio):
        """
        On Utterance Event: Called whenever a person utters something

        Parameters
        ----------
        audio: np.ndarray
            16-bit speech audui
        """

        # Transcribe Audio using Google Speech API
        hypotheses = self.asr.transcribe(audio)

        if hypotheses:

            # Get the most likely Hypothesis
            transcript, confidence = hypotheses[0]

            # Call on Transcript with the Person information
            self.on_transcript(audio, transcript, confidence, self.current_person, self.current_person_confidence)

    def on_transcript(self, audio, transcript, transcript_confidence, name, name_confidence):
        """
        On Transcript Event: Called whenever a person utters something

        Parameters
        ----------
        transcript: str
            Utterance transcript, as obtained from the Google Speech API
        transcript_confidence: float
            Utterance confidence 0..1
        name: str
            Name of Person talking, i.e. last person that was confidently seen by Pepper
        name_confidence: float
            Confidence that the face that was seen actually corresponds to this person -1..+1
        """
        self.log.info('{}: "{}"'.format(name, transcript))

        # Give Random Answer from 'Eloquence'
        # self.say(choice(LAST_RESORT))

        self.say(analyze_utterance(transcript, name if name else "person"))

    def on_person_recognize(self, name, confidence):
        """
        On Person Recognize Event: Called whenever a person in Pepper's Cluster is recognized

        Parameters
        ----------
        name: str
            Name of the person
        confidence: float
            Confidence that this is actually this person -1..+1
        """

        if name != self.current_person:  # Only trigger when known person changes
            self.log.info("Recognized '{}' with Silhouette Score: {}".format(name, confidence))

            # Update Current Person, to which on_transcript will be attributed
            self.current_person = name
            self.current_person_confidence = confidence

            # Greet Person and ask Question
            self.say("Hey {}".format(name))

    def on_person_new(self, confidence):
        """
        On Person New Event: Called when a face has been spotted that is not in Pepper's known people (can be outlier)

        Parameters
        ----------
        confidence: float
            Confidence that Pepper actually does know this person -1..+1
        """
        self.log.info("Recognized New Person with Silhouette Score: {}".format(confidence))

    def say(self, text):
        """
        Let Pepper Say something, animated, logged and easily modifiable speed.

        Parameters
        ----------
        text
        """
        self.log.info('Leolani: "{}"'.format(text))

        self.utterance.stop()
        self.tts.say(r"\\rspd={}\\{}".format(self.TEXT_TO_SPEECH_SPEED, text))
        self.utterance.start()

    def update(self):
        """Continuously take pictures and recognize available faces"""

        while True:
            image = self.camera.get()
            face = self.openface.represent(image)

            if face:
                bounds, representation = face
                name, silhouette_score = self.cluster.classify(representation)

                # If Pepper is sure enough, recognize known/new person
                if silhouette_score > self.PERSON_RECOGNITION_THRESHOLD:
                    self.on_person_recognize(name, silhouette_score)
                elif silhouette_score < self.NEW_PERSON_THRESHOLD:
                    self.on_person_new(silhouette_score)

            sleep(self.CAMERA_FREQUENCY)  # Important to keep the rest working :)


if __name__ == "__main__":
    # Run the Application
    TheoryOfMindApp(pepper.ADDRESS).run()
from pepper.framework import *
from pepper.knowledge import Wikipedia
from pepper import config


class WikipediaApplication(AbstractApplication, StatisticsComponent, StreamedSpeechRecognitionComponent, TextToSpeechComponent):
    def on_transcript(self, hypotheses, audio):
        """
        On Transcript Event.
        Called every time an utterance was understood by Automatic Speech Recognition.

        Parameters
        ----------
        hypotheses: List[ASRHypothesis]
            Hypotheses about the corresponding utterance
        audio: numpy.ndarray
            Utterance audio
        """

        # Choose first ASRHypothesis as Question
        question = hypotheses[0].transcript

        # Query Wikipedia for Answer to Question
        result = Wikipedia.query(question)

        if result:

            answer, url = result
            
            # Limit Answer to a single sentence
            answer = answer.split('.')[0]

            # Tell Answer to Human
            self.say(answer)

        else:

            # Tell Human you don't know
            self.say("I don't know!")


if __name__ == "__main__":

    # Get Backend from Global Configuration File
    backend = config.get_backend()

    # Create Application with given Backend
    application = WikipediaApplication(backend)

    # Run Application
    application.run()

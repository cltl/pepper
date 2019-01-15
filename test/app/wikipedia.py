from pepper.framework import *
from pepper.knowledge.wikipedia import Wikipedia
from pepper import config


class WikipediaApp(AbstractApplication,
                   StatisticsComponent,
                   StreamingSpeechRecognitionComponent,
                   TextToSpeechComponent):

    def on_transcript(self, hypotheses, audio):
        question = hypotheses[0].transcript
        print(question)
        self.respond_wikipedia(question)

    def respond_wikipedia(self, question):
        answer = Wikipedia().query(question)
        if answer:
            answer = answer.split('. ')[0]
            self.say(answer)
        return answer


if __name__ == "__main__":
    WikipediaApp(config.get_backend()).run()
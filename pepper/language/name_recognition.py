import nltk
import os


class NameRecognition(object):

    KEYS = ["PERSON", "ORGANIZATION"]

    def __init__(self):

        ROOT = os.path.join(os.path.dirname(__file__), 'stanford-ner')

        self.ner = nltk.StanfordNERTagger(
            os.path.join(ROOT, 'english.muc.7class.distsim.crf.ser'),
            os.path.join(ROOT, 'stanford-ner.jar'))

    def recognize(self, transcript):
        tokens = nltk.word_tokenize(transcript)
        tags = self.ner.tag(tokens)
        print(tags)
        words = ['{}' if tag in self.KEYS else word for word, tag in tags]
        return ' '.join(words)


if __name__ == "__main__":
    nr = NameRecognition()
    print(nr.recognize("Where does Selena come from"))
    print(nr.recognize("Where does Selene come from"))
    print(nr.recognize("Where does Piek come from"))
    print(nr.recognize("Where does Bram come from"))
    print(nr.recognize("Where does Graham come from"))

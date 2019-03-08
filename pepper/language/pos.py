from nltk.tag.stanford import StanfordPOSTagger
from pepper.config import PACKAGE_ROOT
import os


class POS(object):
    """Part of Speech tagging using Stanford POSTagger"""

    STANFORD_POS = os.path.join(PACKAGE_ROOT, 'language', 'stanford-pos')
    STANFORD_POS_JAR = os.path.join(STANFORD_POS, 'stanford-postagger.jar')
    STANFORD_POS_TAGGER = os.path.join(STANFORD_POS, 'models/english-bidirectional-distsim.tagger')
    
    def __init__(self):
        self._tagger = StanfordPOSTagger(POS.STANFORD_POS_TAGGER, path_to_jar=POS.STANFORD_POS_JAR)

    def tag(self, tokens):
        """
        Tag Part of Speech using Stanford NER

        Parameters
        ----------
        tokens

        Returns
        -------
        POS: list of tuples of strings
        """

        try: return self._tagger.tag(tokens)
        except: return [(token, 'ERROR') for token in tokens]

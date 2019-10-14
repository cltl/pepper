"""
The Pepper Language Package contains tools to generate RDF triples from Natural Language and vice versa.
"""


from .language import Chat, Utterance
from .utils.atoms import UtteranceType


# Download NLTK Dependencies
import nltk

# Make sure Averaged Perceptron Tagger has been downloaded
try: nltk.data.find('taggers/averaged_perceptron_tagger.zip')
except: nltk.download('averaged_perceptron_tagger')

# Make sure Wordnet has been downloaded
try: nltk.data.find('corpora/wordnet.zip')
except: nltk.download('wordnet')

# Make sure Punkt has been downloaded
try: nltk.data.find('tokenizers/punkt.zip')
except: nltk.download('punkt')

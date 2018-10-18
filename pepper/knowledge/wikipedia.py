from nltk.corpus import wordnet as wn
import nltk


import requests
import urllib
import re


class Wikipedia:
    BASE = "https://en.wikipedia.org/w/api.php?format=json" \
           "&action=query&prop=extracts&exintro&explaintext&redirects=1&titles="

    REGEX = re.compile('\(.*?\)')

    def nlp_query(self, query):
        tokens = nltk.word_tokenize(query)
        tokens = [self.lemmatize(word) for word in tokens]

        pos = nltk.pos_tag(tokens)
        pos = self.combine_pos(pos)

        print(pos)

        # If this is a proper question about a Noun
        if pos and pos[0][1].startswith("VB") or pos[0][1] in ["MD"] or pos[0][0].lower() in ["what", "who"]:

            # And there is only one Noun in Question (a.k.a., question is simple enough)
            if sum([tag == "NN" for word, tag in pos]) == 1:

                # Query Wikipedia About last object
                for word, tag in pos[::-1]:
                    if tag.startswith('NN') or tag.startswith("JJ"):
                        return self.query(word)
        return None

    def query(self, query):
        json = requests.get(self.BASE + urllib.quote(query)).json()
        extract = self.find_key(json, 'extract')

        if extract: return re.sub(self.REGEX, '', extract)
        else: return None

    def find_key(self, dictionary, key):
        for k, v in dictionary.items():
            if k == key: return v
            if isinstance(v, dict): return self.find_key(v, key)
        return None

    def combine_pos(self, pos):
        combined_pos = [list(pos[0])]
        for (word, p) in pos[1:]:
            if combined_pos[-1][1] == p:
                combined_pos[-1][0] += " " + word
            else:
                combined_pos.append([word, p])
        return combined_pos

    def lemmatize(self, word):
        synsets = wn.synsets(word)
        if synsets:
            lemmas = synsets[0]._lemma_names
            if lemmas:
                return lemmas[0]
        return word

if __name__ == '__main__':
    synset = wn.synsets("clouds")[0]

    print(dir(synset))
    print(synset._lemma_names[0])
    print(Wikipedia().nlp_query("What are clouds?"))
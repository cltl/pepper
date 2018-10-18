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
        pos = self.combine_pos(nltk.pos_tag(tokens))

        print(pos)

        # Parse proper questions about a noun
        if pos and pos[0][1].startswith("VB") or pos[0][1] in ["MD"] or pos[0][0].lower() in ["what", "who"]:
            for word, tag in pos[::-1]:
                if tag.startswith('NN'):
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


if __name__ == '__main__':
    print(Wikipedia().nlp_query("What is the Eiffel Tower?"))
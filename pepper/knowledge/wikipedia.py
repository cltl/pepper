from __future__ import unicode_literals

import nltk

import requests
import urllib

from random import shuffle
import re


class Wikipedia:

    EXTRACT = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&titles="
    LINKS = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=links&pllimit=max&titles="
    DISAMBIGUATION = "may refer to:"

    PARENTHESES = re.compile('\(.*?\)')
    DUPLICATE_SPACES = re.compile('[ )(]+')

    def nlp_query(self, query):
        tokens = nltk.word_tokenize(query)

        pos = nltk.pos_tag(tokens)
        pos = self.combine_nouns(pos)

        # If this is a proper question about a Noun
        if pos and pos[0][1].startswith("VB") or pos[0][1] in ["MD"] or pos[0][0].lower() in ["what", "who"]:

            # And there is only one Noun in Question (a.k.a., question is simple enough)
            if sum([self.is_queryable(tag) for word, tag in pos]) == 1:

                # Query Wikipedia About last object
                for word, tag in pos[::-1]:
                    if self.is_queryable(tag):
                        answer = self.query(word)
                        if answer:
                            return re.sub(self.DUPLICATE_SPACES, ' ', re.sub(self.PARENTHESES, '', answer))
                        else:
                            return None
        return None

    def query(self, query):
        query_websafe = urllib.quote(query)
        json = requests.get(self.EXTRACT + query_websafe).json()
        extract = self.find_key(json, 'extract')

        if extract:
            if self.DISAMBIGUATION in extract:
                links = self.find_key(requests.get(self.LINKS + query_websafe).json(), 'links')
                shuffle(links)

                for link in links:
                    new_query = link['title']
                    extract = self.query(new_query)
                    if extract:
                        return "{} may refer to {}. {}".format(query, new_query, extract)
            else:
                return extract

    def find_key(self, dictionary, key):
        for k, v in dictionary.items():
            if k == key: return v
            if isinstance(v, dict): return self.find_key(v, key)
        return None

    def combine_nouns(self, pos):
        combined_pos = [list(pos[0])]
        for (word, tag) in pos[1:]:
            if self.is_queryable(tag) and self.is_queryable(combined_pos[-1][1]):
                combined_pos[-1][0] += " " + word
            else:
                combined_pos.append([word, tag])
        return combined_pos

    @staticmethod
    def is_queryable(tag):
        return tag.startswith('NN') or tag.startswith("JJ")
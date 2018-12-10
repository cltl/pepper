from __future__ import unicode_literals

import nltk

from numba import jit
import requests
import urllib

import re


class Wikipedia:

    FULL = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&explaintext&titles="
    SUMMARY = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&titles="
    LINKS = "https://en.wikipedia.org/w/api.php?format=json&action=query&prop=links&pllimit=max&titles="
    THUMBNAIL = "http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&pithumbsize=1000&titles="
    DISAMBIGUATION = "may refer to:"

    PARENTHESES = re.compile('\(.*?\)')
    DUPLICATE_SPACES = re.compile('[ )(]+')

    @staticmethod
    def query(query):
        tokens = nltk.word_tokenize(query)

        pos = nltk.pos_tag(tokens)
        pos = Wikipedia._combine_nouns(pos)

        # If this is a proper question about a Noun
        if pos and pos[0][1].startswith("VB") or pos[0][1] in ["MD"] or pos[0][0].lower() in ["what", "who"]:

            # And there is only one Noun in Question (a.k.a., question is simple enough)
            if sum([Wikipedia._is_queryable(tag) for word, tag in pos]) == 1:

                # Query Wikipedia About last object
                for word, tag in pos[::-1]:
                    if Wikipedia._is_queryable(tag):
                        query, answer, url = Wikipedia._query(word)

                        if answer:
                            answer = re.sub(Wikipedia.DUPLICATE_SPACES, ' ', re.sub(Wikipedia.PARENTHESES, '', answer))
                            return answer, url
                        else:
                            return None
        return None

    @staticmethod
    def _query(query):
        query_websafe = urllib.quote(query)

        # Query Summary
        json = requests.get(Wikipedia.FULL + query_websafe).json()
        extract = Wikipedia._find_key(json, 'extract')

        if extract:
            if Wikipedia.DISAMBIGUATION in extract:
                links = Wikipedia._find_key(requests.get(Wikipedia.LINKS + query_websafe).json(), 'links')

                for link in links:
                    new_query = link['title']
                    extract = Wikipedia._query(new_query)
                    if extract:
                        return "{} may refer to {}: {}".format(query, new_query, extract)
            else:

                # Query Thumbnail
                json = requests.get(Wikipedia.THUMBNAIL + query_websafe).json()
                url = Wikipedia._find_key(json, 'source')

                return query, extract, url


    @staticmethod
    def _find_key(dictionary, key):
        for k, v in dictionary.items():
            if k == key: return v
            if isinstance(v, dict): return Wikipedia._find_key(v, key)
        return None

    @staticmethod
    def _combine_nouns(pos):
        combined_pos = [list(pos[0])]
        for (word, tag) in pos[1:]:
            if Wikipedia._is_queryable(tag) and Wikipedia._is_queryable(combined_pos[-1][1]):
                combined_pos[-1][0] += " " + word
            else:
                combined_pos.append([word, tag])
        return combined_pos

    @staticmethod
    def _is_queryable(tag):
        return tag.startswith('NN') or tag.startswith("JJ")


if __name__ == '__main__':
    from time import time

    N = 10

    t0 = time()
    for i in range(N): Wikipedia.query("Who is Alan Turing?")
    print((time() - t0) / float(N))
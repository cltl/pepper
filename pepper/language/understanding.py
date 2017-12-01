import json

from watson_developer_cloud import NaturalLanguageUnderstandingV1
from watson_developer_cloud.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions

from utils.watson_credentials import NLU


class NaturalLanguageUnderstanding(object):
    def __init__(self):
        """
        Interact with Watson Natural Language Understanding API
        """
        self.NLU = NaturalLanguageUnderstandingV1(
                    version='2017-02-27',
                    username=NLU['username'],
                    password=NLU['password'])

    def analyze(self, text):
        """
        Get features from query, such as keywords (relevance,text) and entities

        Parameters
        ----------
        query: str
            Text to analyze by Watson

        Returns
        -------
        result: json
            Analysis of the query
        """

        analysis = self.NLU.analyze(
            text=text, features=Features(entities=EntitiesOptions(), keywords=KeywordsOptions()))

        return analysis


if __name__ == "__main__":
    print(json.dumps(NaturalLanguageUnderstanding().analyze("I work at Elsevier and I like it"), indent=2))
"""
Query the Wolfram Alpha API using Natural Language.
"""

from pepper import config

import requests


class Wolfram:
    API_SPOKEN = ur"https://api.wolframalpha.com/v1/spoken?appid={}&i={}"
    API_QUERY = ur"http://www.wolframalpha.com/queryrecognizer/query.jsp?&appid={}&mode=Voice&i={}"

    ERRORS = [
        "Wolfram Alpha did not understand your input",
        "No spoken result available",
        "Information about"
    ]

    TOO_BROAD = "Information about "

    def __init__(self):
        """
        Interact with Wolfram Spoken Results API

        Parameters
        ----------
        appid: str
            Wolfram Application Identifier
        """
        self.appid = config.TOKENS['wolfram']

    def is_query(self, query):
        return requests.get(self.API_QUERY.format(self.appid, query.replace(u' ', u'+'))).text

    def query(self, query):
        """
        Get spoken result from WolframAlpha query

        Parameters
        ----------
        query: str
            Question to ask the WolframAlpha Engine

        Returns
        -------
        result: str or None
            Answer to Question or None if no answer could be found
        """

        result = requests.get(self.API_SPOKEN.format(self.appid, query.replace(u' ', u'+'))).text
        if any([result.startswith(error) for error in self.ERRORS]):
            if result.startswith(self.TOO_BROAD):
                topic = result.replace(self.TOO_BROAD, "")
                return "What would you like to know about {}?".format(topic)
        else: return result
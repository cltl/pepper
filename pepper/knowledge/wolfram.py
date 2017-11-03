import requests
import json


class Wolfram:
    API_SPOKEN = r"https://api.wolframalpha.com/v1/spoken?appid={}&i={}"
    API_QUERY = r"http://www.wolframalpha.com/queryrecognizer/query.jsp?&appid={}&i={}"

    ERRORS = [
        "Wolfram Alpha did not understand your input",
        "No spoken result available",
        "Information about"
    ]

    def __init__(self, app = "LA3GP6-VJ8KK8Y36A"):
        """
        Interact with Wolfram Spoken Results API

        Parameters
        ----------
        app: str
            Application Identifier
        """
        self.app = app

    def is_query(self, query):
        return requests.get(self.API_QUERY.format(self.app, query.replace(u' ', u'+'))).text

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

        result = requests.get(self.API_SPOKEN.format(self.app, query.replace(u' ', u'+'))).text
        if any([result.startswith(error) for error in self.ERRORS]): return None
        else: return result


if __name__ == "__main__":
    print(Wolfram().query("Eiffel Tower"))
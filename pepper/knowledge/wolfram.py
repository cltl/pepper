import requests
import re


class SimpleWolfram:
    API = "https://api.wolframalpha.com/v1/spoken?i={}&appid={}"

    ERRORS = [
        "Wolfram Alpha did not understand your input",
        "No spoken result available",
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

    def get(self, query):
        """
        Get spoken result from WolframAlpha query

        Parameters
        ----------
        query: str
            Question to ask the WolframAlpha Engine

        Returns
        -------
        result: str
            Answer to Question or one of SimpleWolfram.ERRORS
        """
        return requests.get(self.API.format(query.replace(u' ', u'+'), self.app)).text


class PodHandler(object):
    def __init__(self, pod, assumptions):
        self._pod = pod
        self._assumption = assumptions

    @property
    def pod(self):
        return self._pod

    @property
    def assumption(self):
        return self._assumption

    def handle(self, json):
        raise NotImplementedError()


class WordDefinitionHandler(PodHandler):

    CATEGORY_ORDER = ['noun', 'verb', 'adjective', 'adverb', 'pronoun',
                      'preposition', 'conjunction', 'determiner', 'exclamation']

    def __init__(self):
        super(WordDefinitionHandler, self).__init__("Definition:WordData", "Word")

    def handle(self, pod):
        words = re.findall(r'([a-zA-Z]+) \| (.+)', pod['subpods'][0]['plaintext'])

        category = {
            'noun': [],
            'verb': [],
            'adjective': [],
            'adverb': [],
            'pronoun': [],
            'preposition': [],
            'conjunction': [],
            'determiner': [],
            'exclamation': []
        }

        for role, word in words:
            category[role].append(word)

        for item in self.CATEGORY_ORDER:
            if category[item]:
                if len(category[item]) == 1:
                    return category[item][0]
                else:
                    return "It can mean {} different things: {}".format(
                        len(category[item]), ", ".join(category[item][:-1]) + " or " + category[item][-1])


class Wolfram:
    API = "https://api.wolframalpha.com/v2/query?appid={}&output=JSON&format=plaintext&input={}{}{}"

    def __init__(self, handlers, app = "LA3GP6-VJ8KK8Y36A"):

        self._simple_wolfram = SimpleWolfram(app)

        self.app = app

        self._handlers = {}
        self._include = ""
        self._assumptions = ""

        for handler in handlers:
            self.add_handler(handler)

    @property
    def simple_wolfram(self):
        return self._simple_wolfram

    @property
    def handlers(self):
        return self._handlers

    @property
    def include(self):
        return self._include

    @property
    def assumptions(self):
        return self._assumptions

    def get(self, query):

        simple_result = self.simple_wolfram.get(query)

        if simple_result not in self.simple_wolfram.ERRORS and not "Information about" in simple_result:
            return simple_result

        call = self.API.format(self.app, query, self.include, self.assumptions)
        result = requests.get(call).json()['queryresult']

        if 'pods' in result:
            for pod in result['pods']:
                return self.handlers[pod['id']].handle(pod)

        if 'assumptions' in result:
            name = [value['name'] for value in result['assumptions']['values']]
            desc = [value['desc'] for value in result['assumptions']['values']]
            code = [value['input'] for value in result['assumptions']['values']]

            for n in name:
                if n in self.handlers:
                    self._assumptions += "&assumption={}".format(code[name.index(n)])
                    return self.get(query)

            return "{} refers to multiple things. It can be {}".format(
                result['assumptions']['word'],
                ", ".join(desc[:-1]) + " or {}".format(desc[-1])
            )

    def add_handler(self, handler):
        self._handlers[handler.pod] = handler
        self._handlers[handler.assumption] = handler
        self._include += "&includepodid={}".format(handler.pod)

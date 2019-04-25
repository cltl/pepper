from SPARQLWrapper import SPARQLWrapper, JSON
import requests


class StoreConnector(object):

    def __init__(self, address, format):
        # type: (str, str) -> StoreConnector
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        self.address = address
        self.format = format

    def upload(self, data):
        """
        Post data to the brain
        :param data: serialized data as string
        :return: response status
        """

        # From serialized string
        post_url = self.address + "/statements"
        response = requests.post(post_url,
                                 data=data,
                                 headers={'Content-Type': 'application/x-' + self.format})

        return str(response.status_code)

    def query(self, query, ask=False):
        # Set up connection
        sparql = SPARQLWrapper(self.address)

        # Response parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addParameter('Accept', 'application/sparql-results+json')
        response = sparql.query().convert()

        if ask:
            return response['boolean']
        else:
            return response["results"]["bindings"]
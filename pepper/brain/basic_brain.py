from pepper.brain.utils.helper_functions import read_query
from pepper.brain.utils.store_connector import StoreConnector
from pepper.brain.utils.rdf_builder import RdfBuilder
from pepper import config, logger

from datetime import datetime


class BasicBrain(object):

    def __init__(self, address=config.BRAIN_URL_LOCAL):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """
        # TODO refactor to use RDF classes
        self._connection = StoreConnector(address, format='trig')
        self._rdf_builder = RdfBuilder()
        self.namespaces = self._rdf_builder.namespaces
        self.dataset = self._rdf_builder.dataset

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted")

        self._brain_log = config.BRAIN_LOG_ROOT.format(datetime.now().strftime('%Y-%m-%d-%H-%M'))

    ########## basic post get behaviour ##########
    def _upload_to_brain(self, data):
        """
        Post data to the brain
        :param data: serialized data as string
        :return: response status
        """
        self._log.debug("Posting triples")

        return self._connection.upload(data)

    def _submit_query(self, query, ask=False):
        """
        Submit a query to the triple store
        Parameters
        ----------
        query: str
            SPARQL query to be posted
        ask: str
            Whether the query is of type ask, in which case the structure of the response changes

        Returns
        -------

        """
        self._log.debug("Posting query")

        return self._connection.query(query, ask=ask)

    ########## brain structure exploration ##########
    def get_predicates(self):
        """
        Get predicates in social ontology
        :return:
        """
        query = read_query('structure exploration/predicates')
        response = self._submit_query(query)

        return [elem['p']['value'].split('/')[-1] for elem in response]

    def get_classes(self):
        """
        Get classes or types in social ontology
        :return:
        """
        query = read_query('structure exploration/classes')
        response = self._submit_query(query)

        return [elem['o']['value'].split('/')[-1] for elem in response]

    def get_labels_and_classes(self):
        """
        Get classes in social ontology
        :return:
        """
        query = read_query('structure exploration/labels_and_classes')
        response = self._submit_query(query)

        temp = dict()
        for r in response:
            temp[r['l']['value']] = r['o']['value'].split('/')[-1]

        return temp

    ########## learned facts exploration ##########
    def count_statements(self):
        """
        Count statements or 'facts' in the brain
        :return:
        """
        query = read_query('content exploration/count_statements')
        response = self._submit_query(query)
        return response[0]['count']['value']

    def count_friends(self):
        """
        Count number of people I have talked to
        :return:
        """
        query = read_query('content exploration/count_friends')
        response = self._submit_query(query)
        return response[0]['count']['value']

    def get_my_friends(self):
        """
        Get names of people I have talked to
        :return:
        """
        query = read_query('content exploration/my_friends')
        response = self._submit_query(query)
        return [elem['name']['value'].split('/')[-1] for elem in response]

    def get_best_friends(self):
        """
        Get names of the 5 people I have talked to the most
        :return:
        """
        query = read_query('content exploration/best_friends')
        response = self._submit_query(query)
        return [elem['name']['value'] for elem in response]

    def when_last_chat_with(self, actor_label):
        """
        Get time value for the last time I chatted with this person
        :param actor_label: name of person
        :return:
        """
        query = read_query('content exploration/when_last_chat_with') % actor_label
        response = self._submit_query(query)

        return response[0]['time']['value'].split('/')[-1] if response != [] else ''

    def get_instance_of_type(self, instance_type):
        """
        Get instances of a certain class type
        :param instance_type: name of class in ontology
        :return:
        """
        query = read_query('content exploration/instance_of_type') % instance_type
        response = self._submit_query(query)
        return [elem['name']['value'] for elem in response] if response else []

    def get_type_of_instance(self, label):
        """
        Get types of a certain instance identified by its label
        :param label: label of instance
        :return:
        """
        query = read_query('content exploration/type_of_instance') % label
        response = self._submit_query(query)
        return [elem['type']['value'] for elem in response] if response else []

    def get_triples_with_predicate(self, predicate):
        """
        Get triples that contain this predicate
        :param predicate:
        :return:
        """
        query = read_query('content exploration/triples_with_predicate') % predicate
        response = self._submit_query(query)
        return [(elem['sname']['value'], elem['oname']['value']) for elem in response]

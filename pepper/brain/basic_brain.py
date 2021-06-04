from pepper.brain.utils.helper_functions import read_query
from pepper.brain.infrastructure import StoreConnector, RdfBuilder
from pepper import config, logger

from datetime import datetime


class BasicBrain(object):
    _ONE_TO_ONE_PREDICATES = [
        'be-from',
        'born_in',
        'favorite',
        'live-in',
        'work-at'
    ]

    _NOT_TO_ASK_PREDICATES = ['faceID', 'name']

    def __init__(self, address=config.BRAIN_URL_LOCAL, clear_all=False, is_submodule=False):
        # type: (str, bool) -> None
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """
        self._connection = StoreConnector(address, format='trig')
        self._rdf_builder = RdfBuilder()

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted")

        self._brain_log = config.BRAIN_LOG_ROOT.format(datetime.now().strftime('%Y-%m-%d-%H-%M'))

        # Start with a clean local memory
        self.clean_local_memory()

        if not is_submodule:
            # Possible clear all contents (testing purposes)
            if clear_all:
                self.clear_brain()

            # Upload ontology here
            self.upload_ontology()

    ########## basic post get behaviour ##########
    def _upload_to_brain(self, data):
        """
        Post data to the brain
        :param data: serialized data as string
        :return: response status
        """
        self._log.info("Posting triples")

        return self._connection.upload(data)

    def _submit_query(self, query, ask=False, post=False):
        """
        Submit a query to the triple store
        Parameters
        ----------
        query: str
            SPARQL query to be posted
        ask: bool
            Whether the query is of type ask, in which case the structure of the response changes

        Returns
        -------

        """
        self._log.debug("Posting query")

        return self._connection.query(query, ask=ask, post=post)

    ########## brain structure exploration ##########
    def _serialize(self, file_path):
        """
        Save graph to local file and return the serialized string
        :param file_path: path to where data will be saved
        :return: serialized data as string
        """
        # Save to file but return the python representation
        with open(file_path + '.' + self._connection.format, 'w') as f:
            self.dataset.serialize(f, format=self._connection.format)

        data = self.dataset.serialize(format=self._connection.format)
        self.clean_local_memory()

        return data

    def upload_ontology(self):
        """
        Upload ontology
        :return: response status
        """
        if not self.ontology_is_uploaded():
            self._rdf_builder.load_ontologies()

            self._log.info("Uploading ontology to brain")
            data = self._serialize(self._brain_log)
            _ = self._connection.upload(data)

    def ontology_is_uploaded(self):
        """
        Query the existance of the Ontology graph, thus not importing the whole Ontology every time
        :return: response status
        """
        self._log.debug("Checking if ontology is in brain")
        query = read_query('structure exploration/ontology_uploaded')
        response = self._submit_query(query, ask=True)

        return response

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

        return [elem['c']['value'].split('/')[-1] for elem in response]

    def get_labels_and_classes(self):
        """
        Get classes in social ontology
        :return:
        """
        query = read_query('structure exploration/labels_and_classes')
        response = self._submit_query(query)

        temp = dict()
        for r in response:
            temp[r['l']['value']] = r['type']['value'].split('/')[-1]

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

    def count_statements_by(self, actor_label):
        """
        Count statements or 'facts' in the brain by a given author
        :return:
        """
        query = read_query('trust/count_statements_by') % actor_label
        response = self._submit_query(query)
        return response[0]['num_stat']['value']

    def novel_statements_by(self, actor_label):
        """
        Return statements or 'facts' in the brain by a given author, that have not been heard from anyone else
        :return:
        """
        query = read_query('trust/novel_statements_by') % actor_label
        response = self._submit_query(query)
        return [elem['stat']['value'].split('/')[-1] for elem in response]

    def get_conflicts(self):
        """
        Count statements or 'facts' in the brain
        :return:
        """
        query = read_query('content exploration/all_conflicts')
        response = self._submit_query(query)
        return response

    def get_conflicts_by(self, actor_label):
        """
        Count statements or 'facts' in the brain
        :return:
        """
        query = read_query('trust/conflicts_by') % (actor_label, actor_label)
        response = self._submit_query(query)
        return response

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
        return [(elem['name']['value'], elem['num_chat']['value'].split('/')[-1]) for elem in response]

    def when_last_chat_with(self, actor_label):
        """
        Get time value for the last time I chatted with this person
        :param actor_label: name of person
        :return:
        """
        query = read_query('trust/when_last_chat_with') % actor_label
        response = self._submit_query(query)

        return response[0]['time']['value'].split('/')[-1] if response != [] else ''

    def count_chat_with(self, actor_label):
        """
        Count times I chatted with this person
        :param actor_label: name of person
        :return:
        """
        query = read_query('trust/count_chat_with') % actor_label
        response = self._submit_query(query)

        return response[0]['num_chats']['value'].split('/')[-1] if response != [] else ''

    def get_instance_of_type(self, instance_type):
        """
        Get instances of a certain class type
        :param instance_type: name of class in ontology
        :return:
        """
        query = read_query('typing/instance_of_type') % instance_type
        response = self._submit_query(query)
        return [elem['name']['value'] for elem in response] if response else []

    def get_type_of_instance(self, label):
        """
        Get types of a certain instance identified by its label
        :param label: label of instance
        :return:
        """
        query = read_query('typing/type_of_instance') % label
        response = self._submit_query(query)
        return [elem['type']['value'] for elem in response] if response else []

    def get_id_of_instance(self, label):
        """
        Get ids of a certain instance identified by its label
        :param label: label of instance
        :return:
        """
        query = read_query('id/id_of_instance') % label
        response = self._submit_query(query)
        return [elem['id']['value'] for elem in response] if response else []

    def get_triples_with_predicate(self, predicate):
        """
        Get triples that contain this predicate
        :param predicate:
        :return:
        """
        query = read_query('content exploration/triples_with_predicate') % predicate
        response = self._submit_query(query)
        return [(elem['sname']['value'], elem['oname']['value']) for elem in response]

    ########## WARNING deletions area ##########

    def clear_brain(self):
        """
        Clear all data from the brain
        :return: response status
        """
        self._log.debug("Clearing brain")
        query = "delete {?s ?p ?o} where {?s ?p ?o .}  "
        _ = self._connection.query(query, post=True)

    def clean_local_memory(self):
        """
        Assign direct access to rdf builder attributes
        Returns
        -------

        """
        self.namespaces = self._rdf_builder.namespaces
        self.dataset = self._rdf_builder.dataset

        self.ontology_graph = self._rdf_builder.ontology_graph
        self.instance_graph = self._rdf_builder.instance_graph
        self.claim_graph = self._rdf_builder.claim_graph
        self.perspective_graph = self._rdf_builder.perspective_graph
        self.interaction_graph = self._rdf_builder.interaction_graph

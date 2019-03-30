from pepper.brain.utils.helper_functions import read_query
from pepper import config, logger

from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Dataset, Namespace, OWL

from datetime import datetime
import requests


class BasicBrain(object):

    def __init__(self, address=config.BRAIN_URL_LOCAL):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """
        # TODO either make connection a class attribute or investigate singleton
        # TODO refactor to use RDF classes
        self.address = address
        self.format = 'trig'
        self.my_uri = None  # NOT USED HERE, ONLY WHEN UPLOADING/EXPERIENCING

        self.namespaces = {}
        self.ontology_paths = {}
        self.dataset = Dataset()

        self.query_prefixes = read_query('prefixes')  # NOT USED HERE, ONLY WHEN QUERYING
        self._define_namespaces()
        self._get_ontology_path()
        self._bind_namespaces()

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted")

        self._brain_log = config.BRAIN_LOG_ROOT.format(datetime.now().strftime('%Y-%m-%d-%H-%M'))

    ########## setting up connection ##########
    def _define_namespaces(self):
        """
        Define namespaces for different layers (ontology/vocab and resource). Assign them to self
        :return:
        """
        # Namespaces for the instance layer
        instance_vocab = 'http://cltl.nl/leolani/n2mu/'
        self.namespaces['N2MU'] = Namespace(instance_vocab)
        instance_resource = 'http://cltl.nl/leolani/world/'
        self.namespaces['LW'] = Namespace(instance_resource)

        # Namespaces for the mention layer
        mention_vocab = 'http://groundedannotationframework.org/gaf#'
        self.namespaces['GAF'] = Namespace(mention_vocab)
        mention_resource = 'http://cltl.nl/leolani/talk/'
        self.namespaces['LTa'] = Namespace(mention_resource)

        # Namespaces for the attribution layer
        attribution_vocab = 'http://groundedannotationframework.org/grasp#'
        self.namespaces['GRASP'] = Namespace(attribution_vocab)
        attribution_resource_friends = 'http://cltl.nl/leolani/friends/'
        self.namespaces['LF'] = Namespace(attribution_resource_friends)
        attribution_resource_inputs = 'http://cltl.nl/leolani/inputs/'
        self.namespaces['LI'] = Namespace(attribution_resource_inputs)

        # Namespaces for the temporal layer-ish
        time_vocab = 'http://www.w3.org/TR/owl-time/#'
        self.namespaces['TIME'] = Namespace(time_vocab)
        time_resource = 'http://cltl.nl/leolani/time/'
        self.namespaces['LTi'] = Namespace(time_resource)

        # The namespaces of external ontologies
        skos = 'http://www.w3.org/2004/02/skos/core#'
        self.namespaces['SKOS'] = Namespace(skos)

        prov = 'http://www.w3.org/ns/prov#'
        self.namespaces['PROV'] = Namespace(prov)

        sem = 'http://semanticweb.cs.vu.nl/2009/11/sem/'
        self.namespaces['SEM'] = Namespace(sem)

        xml = 'https://www.w3.org/TR/xmlschema-2/#'
        self.namespaces['XML'] = Namespace(xml)

    def _get_ontology_path(self):
        """
        Define ontology paths to key vocabularies
        :return:
        """
        self.ontology_paths['n2mu'] = './../../knowledge_representation/ontologies/leolani.ttl'
        self.ontology_paths['gaf'] = './../../knowledge_representation/ontologies/gaf.rdf'
        self.ontology_paths['grasp'] = './../../knowledge_representation/ontologies/grasp.rdf'
        self.ontology_paths['sem'] = './../../knowledge_representation/ontologies/sem.rdf'

    def _bind_namespaces(self):
        """
        Bind namespaces
        :return:
        """
        self.dataset.bind('n2mu', self.namespaces['N2MU'])
        self.dataset.bind('leolaniWorld', self.namespaces['LW'])
        self.dataset.bind('gaf', self.namespaces['GAF'])
        self.dataset.bind('leolaniTalk', self.namespaces['LTa'])
        self.dataset.bind('grasp', self.namespaces['GRASP'])
        self.dataset.bind('leolaniFriends', self.namespaces['LF'])
        self.dataset.bind('leolaniInputs', self.namespaces['LI'])
        self.dataset.bind('time', self.namespaces['TIME'])
        self.dataset.bind('leolaniTime', self.namespaces['LTi'])
        self.dataset.bind('skos', self.namespaces['SKOS'])
        self.dataset.bind('prov', self.namespaces['PROV'])
        self.dataset.bind('sem', self.namespaces['SEM'])
        self.dataset.bind('xml', self.namespaces['XML'])
        self.dataset.bind('owl', OWL)

    ########## basic post get behaviour ##########
    def _upload_to_brain(self, data):
        """
        Post data to the brain
        :param data: serialized data as string
        :return: response status
        """
        self._log.debug("Posting triples")

        # From serialized string
        post_url = self.address + "/statements"
        response = requests.post(post_url,
                                 data=data,
                                 headers={'Content-Type': 'application/x-' + self.format})

        return str(response.status_code)

    def _submit_query(self, query):
        # Set up connection
        sparql = SPARQLWrapper(self.address)

        # Response parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addParameter('Accept', 'application/sparql-results+json')
        response = sparql.query().convert()

        return response["results"]["bindings"]

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
        query = read_query('content exploration/when_last_chat_with') % (actor_label)
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

    def check_statement_existence(self, instance_url):
        query = read_query('content exploration/instance_existence') % (instance_url)
        response = self._submit_query(query)

        if response[0] != {}:
            response = [{'date': elem['date']['value'].split('/')[-1], 'authorlabel': elem['authorlabel']['value']} for elem in response]

        return response
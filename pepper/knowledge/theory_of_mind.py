import subprocess
from rdflib import Dataset, Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from iribaker import to_iri


class TheoryOfMind(object):
    def __init__(self, address, upload_ontology=False):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """
        self.address = "http://145.100.58.167:50053/" if address is None else address
        self.namespaces = {}
        self.dataset = Dataset()

        self.__define_namespaces__()

        if upload_ontology:
            self.__upload_ontology__()

    def __define_namespaces__(self):
        # Namespaces for the instance layer
        instance_vocab = 'http://cltl.nl/leolani/n2mu/'
        self.namespaces['INSTANCE_VOCAB'] = Namespace(instance_vocab)
        instance_resource = 'http://cltl.nl/leolani/world/'
        self.namespaces['INSTANCE_RESOURCE'] = Namespace(instance_resource)

        # Namespaces for the mention layer
        mention_vocab = 'http://groundedannotationframework.org/gaf'
        self.namespaces['MENTION_VOCAB'] = Namespace(mention_vocab)
        mention_resource = 'http://cltl.nl/leolani/talk/'
        self.namespaces['MENTION_RESOURCE'] = Namespace(mention_resource)

        # Namespaces for the attribution layer
        attribution_vocab = 'http://groundedannotationframework.org/grasp'
        self.namespaces['ATTRIBUTION_VOCAB'] = Namespace(attribution_vocab)
        attribution_resource = 'http://cltl.nl/leolani/friends/'
        self.namespaces['ATTRIBUTION_RESOURCE'] = Namespace(attribution_resource)

        # Namespaces for the temporal layer-ish
        time_vocab = 'http://www.w3.org/TR/owl-time#'
        self.namespaces['TIME_VOCAB'] = Namespace(time_vocab)
        time_resource = 'http://cltl.nl/leolani/date/'
        self.namespaces['TIME_RESOURCE'] = Namespace(time_resource)

        # The namespaces of external ontologies
        skos = 'http://www.w3.org/2004/02/skos/core#'
        self.namespaces['SKOS'] = Namespace(skos)

        prov = 'http://www.w3.org/ns/prov#'
        self.namespaces['PROV'] = Namespace(prov)

        sem = 'http://semanticweb.cs.vu.nl/2009/11/sem/'
        self.namespaces['SEM'] = Namespace(sem)

    def __upload_ontology__(self):
        # TODO implement this method
        n2mu_path = './../../knowledge_representation/ontologies/leolani.ttl'

        return n2mu_path

    def _create_instance_layer_(self, instances):
        # TODO Check if this entity exists?
        # TODO how to add types?
        # Subject
        subject = URIRef(to_iri(self.namespaces['INSTANCE_RESOURCE'] + instances['subject']['id']))
        subject_label = Literal(instances['subject']['label'])
        subject_type = URIRef(self.namespaces['INSTANCE_VOCAB'] + instances['subject']['type'])

        self.dataset.add(subject, RDFS.label, subject_label)
        self.dataset.add(subject, RDF.type, subject_type)

        # Object
        object = URIRef(to_iri(self.namespaces['INSTANCE_RESOURCE'] + instances['object']['id']))
        object_label = Literal(instances['object']['label'])
        object_type = URIRef(self.namespaces['INSTANCE_VOCAB'] + instances['object']['type'])

        self.dataset.add(object, RDFS.label, object_label)
        self.dataset.add(object, RDF.type, object_type)

        # Predicate
        # TODO How to access predicates?
        predicate = instances['predicate']['type']

        # Triple
        self.dataset.add(subject, self.namespaces['INSTANCE_VOCAB'][predicate], object)

        return subject, self.namespaces['INSTANCE_VOCAB'][predicate], object

    def _create_statement_(self, triple):
        # Create hashed id from name for this triple
        statement_uri = hash_id(triple)

        # Create graph and add triple
        graph = self.dataset.graph(statement_uri)
        graph.add(triple[0], triple[1], triple[2])

        # TODO Need help with this, what to return?
        return statement_uri

    def _create_mention_layer_(self, mentions, statement, triple):
        # Turn
        turn = URIRef(to_iri(self.namespaces['MENTION_RESOURCE'] + mentions['turn']['id']))
        turn_value = Literal(mentions['turn']['value'])
        turn_type = URIRef(self.namespaces['MENTION_VOCAB'] + 'Mention')

        self.dataset.add(turn, RDF.value, turn_value)
        self.dataset.add(turn, RDF.type, turn_type)

        # Add denotations
        # TODO How to access predicates
        self.dataset.add(statement, self.namespaces['MENTION_VOCAB']['denotedBy'], turn)
        self.dataset.add(triple[0], self.namespaces['MENTION_VOCAB']['denotedIn'], turn)
        self.dataset.add(triple[2], self.namespaces['MENTION_VOCAB']['denotedIn'], turn)

        # Add inverse denotations
        # TODO necessary?
        self.dataset.add(turn, self.namespaces['MENTION_VOCAB']['denotes'], statement)
        self.dataset.add(turn, self.namespaces['MENTION_VOCAB']['containsDenotation'], triple[0])
        self.dataset.add(turn, self.namespaces['MENTION_VOCAB']['containsDenotation'], triple[2])

        return turn

    def _serialize_(self, file_path):
        with open(file_path, 'w') as f:
            self.dataset.serialize(f, format='trig')

    def update(self, parsed_data):
        # TODO: In leolani time create time instance

        # Create instances: In leolaniWorld: add subject, object
        triple = self._create_instance_layer_(parsed_data['instance_layer'])

        # Create statement: In graph (hashed name from triple) create
        statement_uri = self._create_statement_(triple)

        # Create mentions
        # In leolaniTalk: create statement and mentions
        turn_uri = self._create_mention_layer_(parsed_data['mention_layer'], statement_uri, triple)

        # Create attributions
        # In leolani friends: create source, attributions with attributions values

        # serialize and upload

        pass

    def update_with_java(self, source, turn, author_name, subject_label, subject_type, predicate_uri, object_label,
                         object_type, perspective, debug=False):
        """
        Post triples to Triple store. Runs subprocess for java API

        Parameters
        ----------
        source: str
            unique identifier for the chat
        turn: int
            unique identifier for the turn within the chat
        author_name: str
            name of the author of the turn
        subject_label: str
            word that represents the subject label
        subject_type: str
            uri that represents the CLASS for the subject.
            CLASS information is not considered a statement but as interpretation
        predicate_uri: str
            uri that represents the predicate
        object_label: str
            word that represents the object label
        object_type: str
            uri that represents the CLASS for the subject.
            CLASS information is not considered as a statement but as interpretation
        perspective: str
            list of perspective values separated by semicolons
        debug: bool
            print out debug statements

        Returns
        -------
        result: string
            Triples added
        """
        debug_arg = '--debug' if debug else ''

        try:
            parameter_string = '--ks %s --source %s --turn %s --author-name %s ' \
                               '--subject-label %s --subject-type %s ' \
                               '--predicate-uri %s ' \
                               '--object-label %s --object-type %s ' \
                               '--perspective %s ' \
                               '%s' % (self.address, source, str(turn), author_name, subject_label, subject_type,
                                       predicate_uri, object_label, object_type, perspective, debug_arg)

            # Call java API with correct parameters
            result = subprocess.check_output(["java storeGraspStatementInKnowledgeStore", parameter_string])

        except subprocess.CalledProcessError as e:
            result = e.output

        return result

    def query_brain(self, query):
        """
        Get features from query, such as keywords (relevance,text) and entities

        Parameters
        ----------
        query: str
            Query to be executed in the knowledge store

        Returns
        -------
        result: json
            Analysis of the query
        """
        # TODO set up connection

        return 'foo'


def hash_id(triple):
    # TODO smarter hash
    return triple[0] + triple[0] + triple[0]


if __name__ == "__main__":
    print("I'm alive")

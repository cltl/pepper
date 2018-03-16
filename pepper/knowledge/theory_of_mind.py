import subprocess
import json
from rdflib import Dataset, Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL, XSD
from iribaker import to_iri
from SPARQLWrapper import SPARQLWrapper, JSON


class TheoryOfMind(object):
    def __init__(self, address="http://145.100.58.167:50053/", upload_ontology=False):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """
        self.address = address
        self.namespaces = {}
        self.ontology_paths = {}
        self.dataset = Dataset()

        self.__define_namespaces__()
        self.__get_ontology_path__()

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

    def __get_ontology_path__(self):
        self.ontology_paths['n2mu'] = './../../knowledge_representation/ontologies/leolani.ttl'
        self.ontology_paths['gaf'] = './../../knowledge_representation/ontologies/gaf.rdf'
        self.ontology_paths['grasp'] = './../../knowledge_representation/ontologies/grasp.rdf'
        self.ontology_paths['sem'] = './../../knowledge_representation/ontologies/sem.rdf'

    def _bind_namespaces_(self):
        self.dataset.bind('n2mu', self.namespaces['INSTANCE_VOCAB'])
        self.dataset.bind('leolaniWorld', self.namespaces['INSTANCE_RESOURCE'])
        self.dataset.bind('gaf', self.namespaces['MENTION_VOCAB'])
        self.dataset.bind('leolaniTalk', self.namespaces['MENTION_RESOURCE'])
        self.dataset.bind('grasp', self.namespaces['ATTRIBUTION_VOCAB'])
        self.dataset.bind('leolaniFriends', self.namespaces['ATTRIBUTION_RESOURCE'])
        self.dataset.bind('time', self.namespaces['TIME_VOCAB'])
        self.dataset.bind('leolaniTime', self.namespaces['TIME_RESOURCE'])
        self.dataset.bind('skos', self.namespaces['SKOS'])
        self.dataset.bind('prov', self.namespaces['PROV'])
        self.dataset.bind('sem', self.namespaces['SEM'])

        self.dataset.bind('owl', OWL)

        self.dataset.default_context.parse(self.ontology_paths['n2mu'], format='turtle')

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
            self.dataset.serialize(f, format='turtle')

    def _paradiso_simple_model_(self, parsed_statement):
        # Subject
        if len(parsed_statement['subject']) == 1:  # We only get the label
            subject_id = parsed_statement['subject'][0]
            subject_label = parsed_statement['subject'][0]
            subject_vocab = OWL
            subject_type = 'Thing'
        else:
            subject_id = parsed_statement['subject'][0]
            subject_label = parsed_statement['subject'][0]
            subject_vocab = self.namespaces['INSTANCE_VOCAB']
            subject_type = parsed_statement['subject'][1]

        subject = URIRef(to_iri(self.namespaces['INSTANCE_RESOURCE'] + subject_id))
        subject_label = Literal(subject_label)
        subject_type = URIRef(subject_vocab + subject_type)

        self.dataset.add((subject, RDFS.label, subject_label))
        self.dataset.add((subject, RDF.type, subject_type))

        # Object
        if len(parsed_statement['object']) == 1:  # We only get the label
            object_id = parsed_statement['object'][0]
            object_label = parsed_statement['object'][0]
            object_vocab = OWL
            object_type = 'Thing'
        else:
            object_id = parsed_statement['object'][0]
            object_label = parsed_statement['object'][0]
            object_vocab = self.namespaces['INSTANCE_VOCAB']
            object_type = parsed_statement['object'][1]

        object = URIRef(to_iri(self.namespaces['INSTANCE_RESOURCE'] + object_id))
        object_label = Literal(object_label)
        object_type = URIRef(object_vocab + object_type)

        self.dataset.add((object, RDFS.label, object_label))
        self.dataset.add((object, RDF.type, object_type))

        # Predicate
        predicate = parsed_statement['predicate']

        # Triple
        self.dataset.add((subject, self.namespaces['INSTANCE_VOCAB'][predicate], object))

        # Create hashed id from name for this statement
        statement_uri = hash_id([subject, predicate, object])

        # Create graph and add triple
        graph = self.dataset.graph(statement_uri)
        graph.add((subject, self.namespaces['INSTANCE_VOCAB'][predicate], object))


    def update(self, parsed_statement):
        # TODO: In leolani time create time instance

        # Create instances: In leolaniWorld: add subject, object
        # triple = self._create_instance_layer_(parsed_statement['instance_layer'])

        # Create statement: In graph (hashed name from triple) create
        # statement_uri = self._create_statement_(triple)

        # Create mentions
        # In leolaniTalk: create statement and mentions
        # turn_uri = self._create_mention_layer_(parsed_statement['mention_layer'], statement_uri, triple)

        # Create attributions
        # In leolani friends: create source, attributions with attributions values

        # serialize and upload

        # Paradiso use case
        self._paradiso_simple_model_(parsed_statement)

        self._serialize_('./../../knowledge_representation/brainOutput/test.ttl')

        return ''

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

    def _create_query_(self, parsed_question):
        if parsed_question['subject']['label'] == "":
            query = "SELECT ?slabel ?authorlabel " \
                    "WHERE " \
                    "?s n2mu:%s ?o . " \
                    " " \
                    "?s rdf:type n2mu:%s . " \
                    "?s rdfs:label ?slabel . " \
                    " " \
                    "?o rdf:type n2mu:%s . " \
                    "?o rdfs:label '%s' . " \
                    " " \
                    "GRAPH ?g { ?s %s ?o . } " \
                    "?g grasp:denotedBy ?m . " \
                    "?m grasp:wasAttributedTo ?author . " \
                    "?author rdfs:label ?authorlabel " \
                    "}" % (parsed_question['predicate'],
                           parsed_question['subject']['type'],
                           parsed_question['object']['type'], parsed_question['object']['label'],
                           parsed_question['predicate'])
        else:
            query = "SELECT ?authorlabel ?v " \
                    "WHERE " \
                    "?s n2mu:%s ?o . " \
                    " " \
                    "?s rdf:type n2mu:%s . " \
                    "?s rdfs:label %s . " \
                    " " \
                    "?o rdf:type n2mu:%s . " \
                    "?o rdfs:label '%s' . " \
                    " " \
                    "GRAPH ?g { ?s %s ?o . } " \
                    "?g grasp:denotedBy ?m . " \
                    "?m grasp:wasAttributedTo ?author . " \
                    "?author rdfs:label ?authorlabel " \
                    "?m grasp:hasAttribution ?att . " \
                    "?att rdf:value ?v " \
                    "}" % (parsed_question['predicate'],
                           parsed_question['subject']['type'], parsed_question['subject']['label'],
                           parsed_question['object']['type'], parsed_question['object']['label'],
                           parsed_question['predicate'])

        return query

    def query_brain(self, parsed_question):
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
        # Set up connection
        sparql = SPARQLWrapper(self.address)

        # Generate query
        query = self._create_query_(parsed_question)

        # Response parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)

        response = sparql.query().convert()
        response_as_string = json.dumps(response, indent=2)

        return response_as_string


def hash_id(triple):
    # TODO smarter hash
    return triple[0] + triple[1] + triple[2]


if __name__ == "__main__":
    # Sample data
    parsed_statement = {
        "subject": ["Bram", "PERSON"],
        "predicate": "likes",
        "object": ["romantic movies"],
        "author": "Selene"
    }
    parsed_question = {
        "subject": {
            "label": "",
            "type": "PERSON"
        },
        "predicate": "is_from",
        "object": {
            "label": "Italy",
            "type": "LOCATION"
        }
    }

    parsed_question2 = {
        "subject": {
            "label": "Selene",
            "type": "PERSON"
        },
        "predicate": "knows",
        "object": {
            "label": "Piek",
            "type": "PERSON"
        }
    }

    # Create brain connection
    brain = TheoryOfMind()

    # Test statements
    response = brain.update(parsed_statement)

    # Test questions
    # response = brain.query_brain(parsed_question)
    # print(response)
    #
    # response2 = brain.query_brain(parsed_question2)
    # print(response2)

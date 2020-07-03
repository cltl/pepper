from pepper.brain.utils.helper_functions import casefold_text
from pepper.brain.infrastructure import Predicate, Entity, Triple, Provenance
from pepper import logger

from rdflib import Dataset, Namespace, OWL
from rdflib import URIRef, Literal
from iribaker import to_iri

import os


class RdfBuilder(object):
    ONTOLOGY_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../ontologies'))

    def __init__(self):
        # type: () -> None

        self.ontology_paths = {}
        self.namespaces = {}
        self.dataset = Dataset()

        self._log = logger.getChild(self.__class__.__name__)
        self._log.debug("Booted")

        self._define_namespaces()
        self._bind_namespaces()
        self.define_named_graphs()

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
        factuality_vocab = 'http://groundedannotationframework.org/grasp/factuality#'
        self.namespaces['GRASPf'] = Namespace(factuality_vocab)
        sentiment_vocab = 'http://groundedannotationframework.org/grasp/sentiment#'
        self.namespaces['GRASPs'] = Namespace(sentiment_vocab)
        emotion_vocab = 'http://groundedannotationframework.org/grasp/emotion#'
        self.namespaces['GRASPe'] = Namespace(emotion_vocab)
        attribution_resource_friends = 'http://cltl.nl/leolani/friends/'
        self.namespaces['LF'] = Namespace(attribution_resource_friends)
        attribution_resource_inputs = 'http://cltl.nl/leolani/inputs/'
        self.namespaces['LI'] = Namespace(attribution_resource_inputs)

        # Namespaces for the temporal layer-ish
        context_vocab = 'http://cltl.nl/episodicawareness/'
        self.namespaces['EPS'] = Namespace(context_vocab)
        self.namespaces['LC'] = Namespace('http://cltl.nl/leolani/context/')

        # The namespaces of external ontologies
        skos = 'http://www.w3.org/2004/02/skos/core#'
        self.namespaces['SKOS'] = Namespace(skos)

        prov = 'http://www.w3.org/ns/prov#'
        self.namespaces['PROV'] = Namespace(prov)

        sem = 'http://semanticweb.cs.vu.nl/2009/11/sem/'
        self.namespaces['SEM'] = Namespace(sem)

        time = 'http://www.w3.org/TR/owl-time/#'
        self.namespaces['TIME'] = Namespace(time)

        xml = 'https://www.w3.org/TR/xmlschema-2/#'
        self.namespaces['XML'] = Namespace(xml)

        wd = 'http://www.wikidata.org/entity/'
        self.namespaces['WD'] = Namespace(wd)

        wdt = 'http://www.wikidata.org/prop/direct/'
        self.namespaces['WDT'] = Namespace(wdt)

        wikibase = 'http://wikiba.se/ontology#'
        self.namespaces['wikibase'] = Namespace(wikibase)

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
        self.dataset.bind('graspf', self.namespaces['GRASPf'])
        self.dataset.bind('grasps', self.namespaces['GRASPs'])
        self.dataset.bind('graspe', self.namespaces['GRASPe'])
        self.dataset.bind('leolaniFriends', self.namespaces['LF'])
        self.dataset.bind('leolaniInputs', self.namespaces['LI'])

        self.dataset.bind('time', self.namespaces['TIME'])
        self.dataset.bind('eps', self.namespaces['EPS'])
        self.dataset.bind('leolaniContext', self.namespaces['LC'])

        self.dataset.bind('skos', self.namespaces['SKOS'])
        self.dataset.bind('prov', self.namespaces['PROV'])
        self.dataset.bind('sem', self.namespaces['SEM'])
        self.dataset.bind('xml', self.namespaces['XML'])
        self.dataset.bind('owl', OWL)

        self.dataset.bind('wd', self.namespaces['WD'])
        self.dataset.bind('wdt', self.namespaces['WDT'])
        self.dataset.bind('wikibase', self.namespaces['wikibase'])

    def define_named_graphs(self):
        # Instance graph
        self.ontology_graph = self.dataset.graph(self.create_resource_uri('LW', 'Ontology'))
        self.instance_graph = self.dataset.graph(self.create_resource_uri('LW', 'Instances'))
        self.claim_graph = self.dataset.graph(self.create_resource_uri('LW', 'Claims'))
        self.perspective_graph = self.dataset.graph(self.create_resource_uri('LTa', 'Perspectives'))
        self.interaction_graph = self.dataset.graph(self.create_resource_uri('LTa', 'Interactions'))

    def load_ontologies(self):
        self.ontology_graph.parse(location=os.path.join(self.ONTOLOGY_ROOT, 'integration.ttl'), format="turtle")
        self.ontology_graph.parse(location=os.path.join(self.ONTOLOGY_ROOT, 'ceo_original.ttl'), format="turtle")

    def _get_ontology_path(self):
        """
        Define ontology paths to key vocabularies
        :return:
        """
        self.ontology_paths['n2mu'] = os.path.join(self.ONTOLOGY_ROOT, 'leolani.ttl')
        self.ontology_paths['gaf'] = os.path.join(self.ONTOLOGY_ROOT, 'gaf.rdf')
        self.ontology_paths['grasp'] = os.path.join(self.ONTOLOGY_ROOT, 'grasp.rdf')
        self.ontology_paths['sem'] = os.path.join(self.ONTOLOGY_ROOT, 'sem.rdf')

    ########## basic constructors ##########
    def _fix_nlp_types(self, types):
        # type: (list) -> list
        """
        Takes list of types incoming from the NLP pipeline and filters out types that are not semantic but
        syntactic (e.g. adjective)
        Parameters
        ----------
        types: list

        Returns fixed_types: list
        -------

        """
        # TODO here we know if two types are different category (aka noun and verb) we might need to split the triple
        fixed_types = []
        for el in types:
            if len(el) == 1:
                # this was just a char
                fixed_types.append(types.split('.')[-1])
                break
            elif "article" in el or "prep" in el or "adj" in el:
                pass
            elif '.' in el:
                fixed_types.append(el.split('.')[-1])
            else:
                fixed_types.append(el)

        # Hand fixed mappings
        if 'artifact' in fixed_types:
            fixed_types.append('object')

        return fixed_types

    def create_resource_uri(self, namespace, resource_name):
        # type: (str, str) -> str
        """
        Create an URI for the given resource (entity, predicate, named graph, etc) in the given namespace
        Parameters
        ----------
        namespace: str
            Namespace where entity belongs to
        resource_name: str
            Label of resource

        Returns
        -------
        uri: str
            Representing the URI of the resource

        """
        if namespace in self.namespaces.keys():
            uri = URIRef(to_iri(self.namespaces[namespace] + resource_name))
        else:
            uri = URIRef(to_iri('{}:{}'.format(namespace, resource_name)))

        return uri

    def fill_literal(self, value, datatype=None):
        # type: (str, str) -> Literal
        """
        Create an RDF literal given its value and datatype
        Parameters
        ----------
        value: str
            Value of the literal resource
        datatype: str
            Datatype of the literal

        Returns
        -------
            Literal with value and datatype given
        """

        return Literal(value, datatype=datatype) if datatype is not None else Literal(value)

    def fill_entity(self, label, types, namespace='LW', uri=None):
        # type: (str, list, str, str) -> Entity
        """
        Create an RDF entity given its label, types and its namespace
        Parameters
        ----------
        label: str
            Label of entity
        types: List[str]
            List of types for this entity
        uri: str
            URI of the entity, is available (i.e. when extracting concepts from wikidata)
        namespace: str
            Namespace where entity belongs to

        Returns
        -------
            Entity object with given label
        """
        if types in [None, ''] and label != '':
            self._log.warning('Unknown type: {}'.format(label))
            return self.fill_entity_from_label(label, namespace)
        else:
            entity_id = self.create_resource_uri(namespace, label) if not uri else URIRef(to_iri(uri))
            fixed_types = self._fix_nlp_types(types)
            return Entity(entity_id, Literal(label), fixed_types)

    def fill_predicate(self, label, namespace='N2MU', uri=None):
        # type: (str, str, str) -> Predicate
        """
        Create an RDF predicate given its label and its namespace
        Parameters
        ----------
        label: str
            Label of predicate
        uri: str
            URI of the predicate, is available (i.e. when extracting concepts from wikidata)
        namespace:
            Namespace where predicate belongs to

        Returns
        -------

            Predicate object with given label
        """
        predicate_id = self.create_resource_uri(namespace, label) if not uri else URIRef(to_iri(uri))

        return Predicate(predicate_id, Literal(label))

    def fill_entity_from_label(self, label, namespace='LW', uri=None):
        # type: (str, str, str) -> Entity
        """
        Create an RDF entity given its label and its namespace
        Parameters
        ----------
        label: str
            Label of entity
        uri: str
            URI of the entity, is available (i.e. when extracting concepts from wikidata)
        namespace: str
            Namespace where entity belongs to

        Returns
        -------
            Entity object with given label and no type information
        """
        entity_id = self.create_resource_uri(namespace, label) if not uri else URIRef(to_iri(uri))

        return Entity(entity_id, Literal(label), [''])

    def empty_entity(self):
        # type: () -> Entity
        """
        Create an empty RDF entity
        Parameters
        ----------

        Returns
        -------
            Entity object with no label and no type information
        """
        return Entity('', Literal(''), [''])

    def fill_provenance(self, author, date):
        # type: (str, date) -> Provenance
        """
        Structure provenance to pair authors and dates when mentions are created
        Parameters
        ----------
        author: str
            Actor that generated the knowledge
        date: date
            Date when knowledge was generated

        Returns
        -------
            Provenance object containing author and date
        """

        return Provenance(author, date)

    def fill_triple(self, subject_dict, predicate_dict, object_dict, namespace='LW'):
        # type: (dict, dict, dict, str) -> Triple
        """
        Create an RDF entity given its label and its namespace
        Parameters
        ----------
        subject_dict: dict
            Information about label and type of subject
        predicate_dict: dict
            Information about type of predicate
        object_dict: dict
            Information about label and type of object
        namespace: str
            Information about which namespace the entities belongs to

        Returns
        -------
            Entity object with given label
        """
        subject = self.fill_entity(subject_dict['label'], [subject_dict['type']], namespace=namespace)
        predicate = self.fill_predicate(predicate_dict['type'])
        object = self.fill_entity(object_dict['label'], [object_dict['type']], namespace=namespace)

        return Triple(subject, predicate, object)

    def fill_triple_from_label(self, subject_label, predicate, object_label, namespace='LW'):
        # type: (str, str, str, str) -> Triple
        """
        Create an RDF entity given its label and its namespace
        Parameters
        ----------
        subject_label: str
            Information about label of subject
        predicate: str
            Information about predicate
        object_label: str
            Information about label of object
        namespace: str
            Information about which namespace the entities belongs to

        Returns
        -------
            Entity object with given label
        """
        subject = self.fill_entity_from_label(subject_label, namespace=namespace)
        predicate = self.fill_predicate(predicate)
        object = self.fill_entity_from_label(object_label, namespace=namespace)

        return Triple(subject, predicate, object)

    ########## basic reverse engineer ##########
    def label_from_uri(self, uri, namespace='LTi'):
        """
        Extract a label from a resource, by removing the namespace
        Parameters
        ----------
        uri: str
            Resource Identifier
        namespace: str
            prefix to remove

        Returns
        -------
            Label of the entity without the namespace

        """
        # type: (str, str) -> str
        return uri.strip(self.namespaces[namespace])

    def clean_aggregated_types(self, aggregated_types):
        # type: (str) -> list
        """
        Remove prefixes and suffixes of types when URIs include them
        Parameters
        ----------
        aggregated_types: str

        Returns
        -------
            List of clean types

        """
        split_types = aggregated_types.split('|')

        clean_types = []
        for type_uri in split_types:
            if '#' in type_uri:
                [prefix, bare_type] = type_uri.split('#', 1)
            elif '/' in type_uri:
                [prefix, bare_type] = type_uri.rsplit('/', 1)
            else:
                bare_type = type_uri

            bare_type = casefold_text(bare_type, format='triple')
            clean_types.append(bare_type)

        return clean_types

    def clean_aggregated_detections(self, aggregated_detections):
        # type: (str) -> list
        """
        Remove id from detections, if it contains it
        Parameters
        ----------
        aggregated_detections: str
            String containing list of detections

        Returns
        -------
            List of detections without id

        """
        split_detections = aggregated_detections.split('|')

        clean_detections = []
        for detection_label in split_detections:
            if '-' in detection_label:
                [detection_label, detection_id] = detection_label.rsplit('-', 1)
            clean_detections.append(detection_label)

        return clean_detections

from pepper import config
from pepper.brain.utils.helper_functions import hash_statement_id, casefold, casefold_capsule, read_query

from rdflib import Dataset, URIRef, Literal, Namespace, RDF, RDFS, OWL
from iribaker import to_iri
from SPARQLWrapper import SPARQLWrapper, JSON
from fuzzywuzzy import process

import requests
import logging


class LongTermMemory(object):

    ONE_TO_ONE_PREDICATES = [
        'age',
        'born_in',
        'faceID',
        'favorite',
        'favorite_of',
        'id',
        'is_from',
        'manufactured_in',
        'mother_is',
        'name'
    ]

    def __init__(self, address=config.LOCAL_BRAIN):
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
        self.format = 'trig'
        self.dataset = Dataset()
        self.query_prefixes = """
                    prefix gaf: <http://groundedannotationframework.org/gaf#> 
                    prefix grasp: <http://groundedannotationframework.org/grasp#> 
                    prefix leolaniInputs: <http://cltl.nl/leolani/inputs/>
                    prefix leolaniFriends: <http://cltl.nl/leolani/friends/> 
                    prefix leolaniTalk: <http://cltl.nl/leolani/talk/> 
                    prefix leolaniTime: <http://cltl.nl/leolani/time/> 
                    prefix leolaniWorld: <http://cltl.nl/leolani/world/> 
                    prefix n2mu: <http://cltl.nl/leolani/n2mu/> 
                    prefix ns1: <urn:x-rdflib:> 
                    prefix owl: <http://www.w3.org/2002/07/owl#> 
                    prefix prov: <http://www.w3.org/ns/prov#> 
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                    prefix sem: <http://semanticweb.cs.vu.nl/2009/11/sem/> 
                    prefix skos: <http://www.w3.org/2004/02/skos/core#> 
                    prefix time: <http://www.w3.org/TR/owl-time/#> 
                    prefix xml: <http://www.w3.org/XML/1998/namespace> 
                    prefix xml1: <https://www.w3.org/TR/xmlschema-2/#> 
                    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
                    """

        self._define_namespaces()
        self._get_ontology_path()
        self._bind_namespaces()

        self.my_uri = None

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    #################################### Main functions to interact with the brain ####################################

    def update(self, capsule):
        """
        Main function to interact with if a statement is coming into the brain. Takes in a structured parsed statement,
        transforms them to triples, and posts them to the triple store
        :param statement: Structured data of a parsed statement
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Case fold
        capsule = casefold_capsule(capsule)

        # Create graphs and triples
        self._model_graphs_(capsule)

        data = self._serialize(config.BRAIN_LOG)

        code = self._upload_to_brain(data)

        # Create JSON output
        capsule["date"] = str(capsule["date"])
        output = {'response': code, 'statement': capsule}

        return output

    def experience(self, capsule):
        """
        Main function to interact with if a statement is coming into the brain. Takes in a structured parsed statement,
        transforms them to triples, and posts them to the triple store
        :param capsule: Structured data of a parsed statement
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Case fold
        capsule = casefold_capsule(capsule)

        # Create graphs and triples
        self._model_sensor_graphs_(capsule)

        data = self._serialize(config.BRAIN_LOG)

        code = self._upload_to_brain(data)

        # Create JSON output
        capsule["date"] = str(capsule["date"])
        output = {'response': code, 'statement': capsule}

        return output

    def query_brain(self, capsule):
        """
        Main function to interact with if a question is coming into the brain. Takes in a structured parsed question,
        transforms it into a query, and queries the triple store for a response
        :param capsule: Structured data of a parsed question
        :return: json response containing the results of the query, and the original question
        """
        # Case fold
        capsule = casefold_capsule(capsule)

        # Generate query
        query = self._create_query(capsule)

        # Perform query
        response = self._submit_query(query)

        # Create JSON output
        if 'date' in capsule.keys():
            capsule["date"] = str(capsule["date"])
        output = {'response': response, 'question': capsule}

        return output

    def process_visual(self, item, exact_only=True):
        """
        Main function to determine if this item can be recognized by the brain, learned, or none
        :param item:
        :return:
        """

        if casefold(item) in self.get_classes():
            # If this is in the ontology already, create sensor triples directly
            text = 'I know about %s. I will remember this object' % item
            return item, text

        temp = self.get_labels_and_classes()
        if casefold(item) in temp.keys():
            # If this is in the ontology already, create sensor triples directly
            text = 'I know about %s. It is of type %s. I will remember this object' % (item, temp[item])
            return item, text

        # Query the web for information
        class_type, description = self.exact_match_dbpedia(item)
        if class_type is not None:
            # Had to learn it, but I can create triples now
            text = 'I did not know what %s is, but I searched on the web and I found that it is a %s. ' \
                   'I will remember this object' % (item, class_type)
            return casefold(class_type), text

        if not exact_only:
            # Second go at dbpedia, relaxed approach
            class_type, description = self.keyword_match_dbpedia(item)
            if class_type is not None:
                # Had to really search for it to learn it, but I can create triples now
                text = 'I did not know what %s is, but I searched for fuzzy matches on the web and I found that it ' \
                       'is a %s. I will remember this object' % (item, class_type)
                return casefold(class_type), text

        # Failure, nothing found
        text = 'I am sorry, I could not learn anything on %s so I will not remember it' % item
        return None, text

    ########## management system for keeping track of chats and turns ##########
    def get_last_chat_id(self):
        """
        Get the id for the last interaction recorded
        :return: id
        """
        query = read_query('last_chat_id')
        response = self._submit_query(query)

        return int(response[0]['chatid']['value']) if response else 0

    def get_last_turn_id(self, chat_id):
        """
        Get the id for the last turn in the given chat
        :param chat_id: id for chat of interest
        :return:  id
        """
        query = read_query('last_turn_id') % (chat_id)
        response = self._submit_query(query)

        last_turn = 0
        for turn in response:
            turn_uri = turn['s']['value']
            turn_id = turn_uri.split('/')[-1][10:]
            turn_id = int(turn_id)

            if turn_id > last_turn:
                last_turn = turn_id

        return last_turn

    ########## brain structure exploration ##########
    def get_predicates(self):
        """
        Get predicates in social ontology
        :return:
        """
        query = read_query('predicates')
        response = self._submit_query(query)

        return [elem['p']['value'].split('/')[-1] for elem in response]

    def get_classes(self):
        """
        Get classes in social ontology
        :return:
        """
        query = read_query('classes')
        response = self._submit_query(query)

        return [elem['o']['value'].split('/')[-1] for elem in response]

    def get_labels_and_classes(self):
        """
        Get classes in social ontology
        :return:
        """
        query = read_query('labels_and_classes')
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
        query = read_query('count_statements')
        response = self._submit_query(query)
        return response[0]['count']['value']

    def count_friends(self):
        """
        Count number of people I have talked to
        :return:
        """
        query = read_query('count_friends')
        response = self._submit_query(query)
        return response[0]['count']['value']

    def get_my_friends(self):
        """
        Get names of people I have talked to
        :return:
        """
        query = read_query('my_friends')
        response = self._submit_query(query)
        return [elem['name']['value'].split('/')[-1] for elem in response]

    def get_best_friends(self):
        """
        Get names of the 5 people I have talked to the most
        :return:
        """
        query = read_query('best_friends')
        response = self._submit_query(query)
        return [elem['name']['value'] for elem in response]

    def get_instance_of_type(self, instance_type):
        """
        Get isntances of a certain class type
        :param instance_type: name of class in ontology
        :return:
        """
        query = read_query('instance_of_type') % (instance_type)
        response = self._submit_query(query)
        return [elem['name']['value'] for elem in response]

    def when_last_chat_with(self, actor_label):
        """
        Get time value for the last time I chatted with this person
        :param actor_label: name of person
        :return:
        """
        query = read_query('when_last_chat_with') % (actor_label)
        response = self._submit_query(query)
        return response[0]['time']['value'].split('/')[-1]

    def get_triples_with_predicate(self, predicate):
        """
        Get triples that contain this predicate
        :param predicate:
        :return:
        """
        query = read_query('triples_with_predicate') % predicate
        response = self._submit_query(query)
        return [(elem['sname']['value'], elem['oname']['value']) for elem in response]

    ########## conflicts ##########
    def get_all_conflicts(self):
        """
        Aggregate all conflicts in brain
        :return:
        """
        conflicts = []
        for predicate in self.ONE_TO_ONE_PREDICATES:
            conflicts.extend(self._get_conflicts_with_predicate(predicate))

        return conflicts

    ########## semantic web ##########
    def exact_match_dbpedia(self, item):
        """
        Query dbpedia for information on this item to get it's semantic type and description.
        :param item:
        :return:
        """

        # Gather combinations
        combinations = [item, item.lower(), item.capitalize(), item.title()]

        for comb in combinations:
            # Try exact matching query
            query = read_query('dbpedia_type_and_description') % (comb)
            response = self._submit_query(query)

            # break if we have a hit
            if response:
                break

        class_type = response[0]['label_type']['value'] if response else None
        description = response[0]['description']['value'].split('.')[0] if response else None

        return class_type, description

    def keyword_match_dbpedia(self, item):
        # Query API
        r = requests.get('http://lookup.dbpedia.org/api/search.asmx/KeywordSearch',
                         params={'QueryString': item, 'MaxHits': '10'},
                         headers={'Accept': 'application/json'}).json()['results']

        # Fuzzy match
        choices = [e['label'] for e in r]
        best_match = process.extractOne("item", choices)

        # Get best match object
        r = [{'label': e['label'], 'classes': e['classes'],'description': e['description']} for e in r if e['label'] == best_match[0]]

        if r:
            r = r[0]

            if r['classes']:
                # process dbpedia classes only
                r['classes'] = [c['label'] for c in r['classes'] if 'dbpedia' in c['uri']]

        else:
            r = {'label': None, 'classes': None,'description': None}


        return r['classes'][0] if r['classes'] else None, r['description'].split('.')[0] if r['description'] else None


    ######################################## Helpers for setting up connection ########################################

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
        Bnd namespaces
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

    ######################################## Helpers for statement processing ########################################

    def create_chat_id(self, actor, date):
        """
        Determine chat id depending on my last conversation with this person
        :param actor:
        :param date:
        :return:
        """
        self._log.debug('Chat with {} on {}'.format(actor, date))

        query = read_query('last_chat_with') % (actor)
        response = self._submit_query(query)

        if response and int(response[0]['day']['value']) == int(date.day) \
                and int(response[0]['month']['value']) == int(date.month) \
                and int(response[0]['year']['value']) == int(date.year):
            # Chatted with this person today so same chat id
            chat_id = int(response[0]['chatid']['value'])
        else:
            # Either have never chatted with this person, or I have but not today. Add one to latest chat
            chat_id = self.get_last_chat_id() + 1

        return chat_id

    def create_turn_id(self, chat_id):
        self._log.debug('Turn in chat {}'.format(chat_id))

        query = read_query('last_turn_in_chat') % (chat_id)
        response = self._submit_query(query)
        return int(response['turnid']['value']) + 1 if response else 1

    def _generate_leolani(self, instance_graph):
        # Create Leolani
        leolani_id = 'leolani'
        leolani_label = 'leolani'

        leolani = URIRef(to_iri(self.namespaces['LW'] + leolani_id))
        leolani_label = Literal(leolani_label)
        leolani_type1 = URIRef(to_iri(self.namespaces['N2MU'] + 'robot'))
        leolani_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((leolani, RDFS.label, leolani_label))
        instance_graph.add((leolani, RDF.type, leolani_type1))
        instance_graph.add((leolani, RDF.type, leolani_type2))

        self.my_uri = leolani

        return leolani

    def _generate_subject(self, capsule, instance_graph):
        if capsule['subject']['type'] == '':  # We only get the label
            subject_vocab = OWL
            subject_type = 'Thing'
        else:
            subject_vocab = self.namespaces['N2MU']
            subject_type = capsule['subject']['type']

        subject_id = capsule['subject']['label']

        subject = URIRef(to_iri(self.namespaces['LW'] + subject_id))
        subject_label = Literal(subject_id)
        subject_type1 = URIRef(to_iri(subject_vocab + subject_type))
        subject_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((subject, RDFS.label, subject_label))
        instance_graph.add((subject, RDF.type, subject_type1))
        instance_graph.add((subject, RDF.type, subject_type2))

        return subject, subject_label

    def _create_leolani_world(self, capsule, type='Statement'):
        # Instance graph
        instance_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'Instances'))
        instance_graph = self.dataset.graph(instance_graph_uri)

        # Subject
        if type == 'Statement':
            subject, subject_label = self._generate_subject(capsule, instance_graph)
        elif type == 'Experience':
            subject = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri
            subject_label = 'leolani'

        # Object
        if capsule['object']['type'] == '':  # We only get the label
            object_vocab = OWL
            object_type = 'Thing'
        else:
            object_vocab = self.namespaces['N2MU']
            object_type = capsule['object']['type']

        object_id = capsule['object']['label']

        object = URIRef(to_iri(self.namespaces['LW'] + object_id))
        object_label = Literal(object_id)
        object_type1 = URIRef(to_iri(object_vocab + object_type))
        object_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((object, RDFS.label, object_label))
        instance_graph.add((object, RDF.type, object_type1))
        instance_graph.add((object, RDF.type, object_type2))

        if type == 'Statement':
            claim_graph, statement = self._create_claim_graph(subject, subject_label, object, object_label,
                                                          capsule['predicate']['type'], type='Statement')
        elif type == 'Experience':
            claim_graph, statement = self._create_claim_graph(subject, subject_label, object, object_label,
                                                               'sees', type='Experience')

        return instance_graph, claim_graph, subject, object, statement

    def _create_claim_graph(self, subject, subject_label, object, object_label, predicate, type='Statement'):
        # Claim graph
        claim_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'Claims'))
        claim_graph = self.dataset.graph(claim_graph_uri)

        # Statement
        statement_id = hash_statement_id([subject_label, predicate, object_label])

        statement = URIRef(to_iri(self.namespaces['LW'] + statement_id))
        statement_type1 = URIRef(to_iri(self.namespaces['GRASP'] + type))
        statement_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))
        statement_type3 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))

        # Create graph and add triple
        graph = self.dataset.graph(statement)
        graph.add((subject, self.namespaces['N2MU'][predicate], object))

        claim_graph.add((statement, RDF.type, statement_type1))
        claim_graph.add((statement, RDF.type, statement_type2))
        claim_graph.add((statement, RDF.type, statement_type3))

        return claim_graph, statement

    def _create_leolani_talk(self, capsule, leolani, type='Statement'):
        # Interaction graph
        interaction_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Interactions'))
        interaction_graph = self.dataset.graph(interaction_graph_uri)

        # Time
        date = capsule["date"]
        time = URIRef(to_iri(self.namespaces['LTi'] + str(capsule["date"].isoformat())))
        time_type = URIRef(to_iri(self.namespaces['TIME'] + 'DateTimeDescription'))
        day = Literal(date.day, datatype=self.namespaces['XML']['gDay'])
        month = Literal(date.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = Literal(date.year, datatype=self.namespaces['XML']['gYear'])
        time_unitType = URIRef(to_iri(self.namespaces['TIME'] + 'unitDay'))

        interaction_graph.add((time, RDF.type, time_type))
        interaction_graph.add((time, self.namespaces['TIME']['day'], day))
        interaction_graph.add((time, self.namespaces['TIME']['month'], month))
        interaction_graph.add((time, self.namespaces['TIME']['year'], year))
        interaction_graph.add((time, self.namespaces['TIME']['unitType'], time_unitType))

        # Actor
        actor_id = capsule['author']
        actor_label = capsule['author']

        actor = URIRef(to_iri(to_iri(self.namespaces['LF'] + actor_id)))
        actor_label = Literal(actor_label)
        actor_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Actor'))
        actor_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))
        if type == 'Statement':
            actor_type3 = URIRef(to_iri(self.namespaces['N2MU'] + 'person'))
        elif type == 'Experience':
            actor_type3 = URIRef(to_iri(self.namespaces['N2MU'] + 'sensor'))
        else:
            actor_type3 = URIRef(to_iri(OWL + 'Thing'))

        interaction_graph.add((actor, RDFS.label, actor_label))
        interaction_graph.add((actor, RDF.type, actor_type1))
        interaction_graph.add((actor, RDF.type, actor_type2))
        interaction_graph.add((actor, RDF.type, actor_type3))

        # Add leolani knows actor
        interaction_graph.add((leolani, self.namespaces['N2MU']['knows'], actor))
        _, _ = self._create_claim_graph(leolani, 'leolani', actor, actor_label,
                                                          'knows', type='Statement')

        # Chat and turn
        chat_id = self.create_chat_id(actor_label, date)
        chat_label = 'chat%s' % chat_id
        turn_id = self.create_turn_id(chat_id)
        turn_label = chat_label + '_turn%s' % turn_id

        turn = URIRef(to_iri(self.namespaces['LTa'] + turn_label))
        turn_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        turn_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Turn'))

        interaction_graph.add((turn, RDF.type, turn_type1))
        interaction_graph.add((turn, RDF.type, turn_type2))
        interaction_graph.add((turn, self.namespaces['N2MU']['id'], Literal(turn_id)))
        interaction_graph.add((turn, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((turn, self.namespaces['SEM']['hasTime'], time))

        chat = URIRef(to_iri(self.namespaces['LTa'] + chat_label))
        chat_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        chat_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Chat'))

        interaction_graph.add((chat, RDF.type, chat_type1))
        interaction_graph.add((chat, RDF.type, chat_type2))
        interaction_graph.add((chat, self.namespaces['N2MU']['id'], Literal(chat_id)))
        interaction_graph.add((chat, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((chat, self.namespaces['SEM']['hasTime'], time))
        interaction_graph.add((chat, self.namespaces['SEM']['hasSubevent'], turn))

        perspective_graph, mention, attribution = self._create_perspective_graph(capsule, turn_label)

        # Link interactions and perspectives
        perspective_graph.add((mention, self.namespaces['GRASP']['wasAttributedTo'], actor))
        perspective_graph.add((mention, self.namespaces['GRASP']['hasAttribution'], attribution))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], chat))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], turn))

        return interaction_graph, perspective_graph, actor, time, mention, attribution

    def _create_perspective_graph(self, parsed_statement, turn_label):
        # Perspective graph
        perspective_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Perspectives'))
        perspective_graph = self.dataset.graph(perspective_graph_uri)

        # Mention
        mention_id = turn_label + '_char%s' % parsed_statement['position']
        mention = URIRef(to_iri(self.namespaces['LTa'] + mention_id))
        mention_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Mention'))

        perspective_graph.add((mention, RDF.type, mention_type))

        # Attribution
        attribution_id = mention_id + '_CERTAIN'
        attribution = URIRef(to_iri(self.namespaces['LTa'] + attribution_id))
        attribution_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Attribution'))
        attribution_value = URIRef(to_iri(self.namespaces['GRASP'] + 'CERTAIN'))

        perspective_graph.add((attribution, RDF.type, attribution_type))
        perspective_graph.add((attribution, RDF.value, attribution_value))

        return perspective_graph, mention, attribution

    def _serialize(self, file_path):
        """
        Save graph to local file and return the serialized string
        :param file_path: path to where data will be saved
        :return: serialized data as string
        """
        # Save to file but return the python representation
        with open(file_path + '.' + self.format, 'w') as f:
            self.dataset.serialize(f, format=self.format)
        return self.dataset.serialize(format=self.format)

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

    def _model_graphs_(self, capsule):
        # Leolani world (includes instance and claim graphs)
        instance_graph, claim_graph, subject, object, statement = self._create_leolani_world(capsule)

        # Identity
        leolani = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri

        # Leolani talk (includes interaction and perspective graphs)
        interaction_graph, perspective_graph, actor, time, mention, attribution = self._create_leolani_talk(capsule, leolani)

        # Interconnections
        instance_graph.add((subject, self.namespaces['GRASP']['denotedIn'], mention))
        instance_graph.add((object, self.namespaces['GRASP']['denotedIn'], mention))

        instance_graph.add((statement, self.namespaces['GRASP']['denotedBy'], mention))
        instance_graph.add((statement, self.namespaces['SEM']['hasActor'], actor))
        instance_graph.add((statement, self.namespaces['SEM']['hasTime'], time))

        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], subject))
        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], object))
        perspective_graph.add((mention, self.namespaces['GRASP']['denotes'], statement))

        perspective_graph.add((attribution, self.namespaces['GRASP']['isAttributionFor'], mention))

    ######################################### Helpers for question processing #########################################

    def _create_query(self, parsed_question):
        _ = hash_statement_id([parsed_question['subject']['label'], parsed_question['predicate']['type'], parsed_question['object']['label']])

        # Query subject
        if parsed_question['subject']['label'] == "":
            # Case fold
            # object_label = casefold_label(parsed_question['object']['label'])

            query = """
                SELECT ?slabel ?authorlabel
                        WHERE { 
                            ?s n2mu:%s ?o . 
                            ?s rdfs:label ?slabel . 
                            ?o rdfs:label '%s' .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['object']['label'],
                       parsed_question['predicate']['type'])

        # Query object
        elif parsed_question['object']['label'] == "":
            query = """
                SELECT ?olabel ?authorlabel
                        WHERE { 
                            ?s n2mu:%s ?o .   
                            ?s rdfs:label '%s' .  
                            ?o rdfs:label ?olabel .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['subject']['label'],
                       parsed_question['predicate']['type'])

        # Query existence
        else:
            query = """
                SELECT ?authorlabel ?v
                        WHERE { 
                            ?s n2mu:%s ?o .   
                            ?s rdfs:label '%s' .  
                            ?o rdfs:label '%s' .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                            ?m grasp:hasAttribution ?att .
                            ?att rdf:value ?v .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['subject']['label'],
                       parsed_question['object']['label'],
                       parsed_question['predicate']['type'])

        query = self.query_prefixes + query

        return query

    def _submit_query(self, query):
        # Set up connection
        sparql = SPARQLWrapper(self.address)

        # Response parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addParameter('Accept', 'application/sparql-results+json')
        response = sparql.query().convert()

        return response["results"]["bindings"]

    ########################################## Helpers for sensor processing ##########################################

    def _create_leolani_talk_sens(self, sensed_visual, leolani):
        # Interaction graph
        interaction_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Sensors'))
        interaction_graph = self.dataset.graph(interaction_graph_uri)

        # Time
        date = sensed_visual["date"]
        time = URIRef(to_iri(self.namespaces['LTi'] + str(sensed_visual["date"].isoformat())))
        time_type = URIRef(to_iri(self.namespaces['TIME'] + 'DateTimeDescription'))
        day = Literal(date.day, datatype=self.namespaces['XML']['gDay'])
        month = Literal(date.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = Literal(date.year, datatype=self.namespaces['XML']['gYear'])
        time_unitType = URIRef(to_iri(self.namespaces['TIME'] + 'unitDay'))

        interaction_graph.add((time, RDF.type, time_type))
        interaction_graph.add((time, self.namespaces['TIME']['day'], day))
        interaction_graph.add((time, self.namespaces['TIME']['month'], month))
        interaction_graph.add((time, self.namespaces['TIME']['year'], year))
        interaction_graph.add((time, self.namespaces['TIME']['unitType'], time_unitType))

        # Actor
        actor_id = sensed_visual['author']
        actor_label = sensed_visual['author']

        actor = URIRef(to_iri(to_iri(self.namespaces['LI'] + actor_id)))
        actor_label = Literal(actor_label)
        actor_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Actor'))
        actor_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        interaction_graph.add((actor, RDFS.label, actor_label))
        interaction_graph.add((actor, RDF.type, actor_type1))
        interaction_graph.add((actor, RDF.type, actor_type2))

        # TODO Add leolani sensed new
        interaction_graph.add((leolani, self.namespaces['N2MU']['sense'], actor))

        # Chat and turn
        chat_id = self.create_chat_id(actor_label, date)
        chat_label = 'visual%s' % chat_id
        turn_id = self.create_turn_id(chat_id)
        turn_label = chat_label + '_object%s' % turn_id

        turn = URIRef(to_iri(self.namespaces['LTa'] + turn_label))
        turn_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        turn_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Object'))

        interaction_graph.add((turn, RDF.type, turn_type1))
        interaction_graph.add((turn, RDF.type, turn_type2))
        interaction_graph.add((turn, self.namespaces['N2MU']['id'], Literal(turn_id)))
        interaction_graph.add((turn, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((turn, self.namespaces['SEM']['hasTime'], time))

        chat = URIRef(to_iri(self.namespaces['LTa'] + chat_label))
        chat_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        chat_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Visual'))

        interaction_graph.add((chat, RDF.type, chat_type1))
        interaction_graph.add((chat, RDF.type, chat_type2))
        interaction_graph.add((chat, self.namespaces['N2MU']['id'], Literal(chat_id)))
        interaction_graph.add((chat, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((chat, self.namespaces['SEM']['hasTime'], time))
        interaction_graph.add((chat, self.namespaces['SEM']['hasSubevent'], turn))

        perspective_graph, mention, attribution = self._create_perspective_graph_sens(sensed_visual, turn_label)

        # Link interactions and perspectives
        perspective_graph.add((mention, self.namespaces['GRASP']['wasAttributedTo'], actor))
        perspective_graph.add((mention, self.namespaces['GRASP']['hasAttribution'], attribution))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], chat))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], turn))

        return interaction_graph, perspective_graph, actor, time, mention, attribution

    def _create_perspective_graph_sens(self, sensed_visual, turn_label):
        # Perspective graph
        perspective_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Perspectives'))
        perspective_graph = self.dataset.graph(perspective_graph_uri)

        # Mention
        mention_id = turn_label + '_pixel%s' % sensed_visual['position']
        mention = URIRef(to_iri(self.namespaces['LTa'] + mention_id))
        mention_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Mention'))

        perspective_graph.add((mention, RDF.type, mention_type))

        # Attribution
        attribution_id = mention_id + '_CERTAIN'
        attribution = URIRef(to_iri(self.namespaces['LTa'] + attribution_id))
        attribution_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Attribution'))
        attribution_value = URIRef(to_iri(self.namespaces['GRASP'] + 'CERTAIN'))

        perspective_graph.add((attribution, RDF.type, attribution_type))
        perspective_graph.add((attribution, RDF.value, attribution_value))

        return perspective_graph, mention, attribution

    def _model_sensor_graphs_(self, experience):
        # Leolani world (includes instance and claim graphs)
        instance_graph, claim_graph, subject, object, statement = self._create_leolani_world(experience, type='Experience')

        # Identity
        leolani = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri

        # Leolani talk (includes interaction and perspective graphs)
        interaction_graph, perspective_graph, actor, time, mention, attribution = self._create_leolani_talk_sens(experience, leolani)

        # Interconnections
        instance_graph.add((subject, self.namespaces['GRASP']['denotedIn'], mention))
        instance_graph.add((object, self.namespaces['GRASP']['denotedIn'], mention))

        instance_graph.add((statement, self.namespaces['GRASP']['denotedBy'], mention))
        instance_graph.add((statement, self.namespaces['SEM']['hasActor'], actor))
        instance_graph.add((statement, self.namespaces['SEM']['hasTime'], time))

        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], subject))
        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], object))
        perspective_graph.add((mention, self.namespaces['GRASP']['denotes'], statement))

        perspective_graph.add((attribution, self.namespaces['GRASP']['isAttributionFor'], mention))


    ######################################### Helpers for conflict processing #########################################
    def _get_conflicts_with_predicate(self, one_to_one_predicate):
        query = """
            PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX grasp: <http://groundedannotationframework.org/grasp#>

            select ?sname 
                    (group_concat(?oname ; separator=";") as ?onames) 
                    (group_concat(?authorlabel ; separator=";") as ?authorlabels) 
            where { 
                GRAPH ?g {
                    ?s n2mu:%s ?o .
                    } .
                ?s rdfs:label ?sname .
                ?o rdfs:label ?oname .

                ?g grasp:denotedBy ?m . 
                ?m grasp:wasAttributedTo ?author . 
                ?author rdfs:label ?authorlabel .

            } group by ?sname having (count(distinct ?oname) > 1)
        """ % one_to_one_predicate

        response = self._submit_query(query)
        conflicts = []
        for item in response:
            conflict = {'subject': item['sname']['value'], 'predicate': one_to_one_predicate, 'objects': []}

            values = item['onames']['value'].split(';')
            authors = item['authorlabels']['value'].split(';')

            for val, auth in zip(values, authors):
                option = {'value': val, 'author': auth}
                conflict['objects'].append(option)

            conflicts.append(conflict)

        return conflicts

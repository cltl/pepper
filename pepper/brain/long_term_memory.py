from pepper.brain.utils.helper_functions import hash_statement_id, casefold, read_query, casefold_capsule, date_from_uri
from pepper.brain.utils.response import Predicate, Entity, Provenance, CardinalityConflict, NegationConflict, \
    StatementNovelty, EntityNovelty
from pepper.brain.basic_brain import BasicBrain
from pepper import config

from rdflib import URIRef, Literal, RDF, RDFS, OWL
from iribaker import to_iri
from fuzzywuzzy import process

import requests


class LongTermMemory(BasicBrain):

    _ONE_TO_ONE_PREDICATES = [
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

    _NOT_TO_ASK_PREDICATES = ['faceID', 'name']

    def __init__(self, address=config.BRAIN_URL_LOCAL):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        super(LongTermMemory, self).__init__(address)

        # Launch first query
        self.count_statements()

    #################################### Main functions to interact with the brain ####################################

    def update(self, capsule):
        """
        Main function to interact with if a statement is coming into the brain. Takes in a structured capsule containing
        a parsed statement, transforms them to triples, and posts them to the triple store
        :param capsule: Structured data of a parsed statement
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Case fold
        capsule = casefold_capsule(capsule, format='triple')

        # Create graphs and triples
        subject_url, object_url, instance_url = self._model_graphs_(capsule)

        # Check if this knowledge already exists on the brain
        statement_novelty = self.get_statement_novelty(instance_url)

        # Check how many items of the same type as subject and object we have
        entity_novelty = self._fill_entity_novelty_(subject_url, object_url)

        # Find any overlaps
        overlaps = self.get_overlaps(capsule)

        # Finish process of uploading new knowledge to the triple store
        data = self._serialize(self._brain_log)
        code = self._upload_to_brain(data)

        # Check for conflicts after adding the knowledge
        negation_conflicts = self.get_negation_conflicts_with_statement(capsule)
        object_conflict = self.get_object_cardinality_conflicts_with_statement(capsule)

        # Check for gaps, in case we want to be proactive
        subject_gaps = self.get_gaps_from_entity(capsule['subject'])
        object_gaps = self.get_gaps_from_entity(capsule['object'])

        # Report trust
        trust = 0 if self.when_last_chat_with(capsule['author']) == '' else 1

        # Create JSON output
        capsule["date"] = str(capsule["date"])
        output = {'response': code, 'statement': capsule,
                  'statement_novelty': statement_novelty,
                  'entity_novelty': entity_novelty,
                  'negation_conflicts': negation_conflicts,
                  'cardinality_conflicts': object_conflict,
                  'subject_gaps': subject_gaps,
                  'object_gaps': object_gaps,
                  'overlaps': overlaps,
                  'trust': trust}

        return output

    def experience(self, capsule):
        """
        Main function to interact with if an experience is coming into the brain. Takes in a structured capsule
        containing parsed experience, transforms them to triples, and posts them to the triple store
        :param capsule: Structured data of a parsed experience
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Case fold
        capsule = casefold_capsule(capsule, format='triple')

        # Create graphs and triples
        subject_url, object_url, instance_url = self._model_graphs_(capsule, type='Experience')
        data = self._serialize(self._brain_log)
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
        capsule = casefold_capsule(capsule, format='triple')

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

        if casefold(item, format='triple') in self.get_classes():
            # If this is in the ontology already as a class, create sensor triples directly
            text = 'I know about %s. I will remember this object' % item
            return item, text

        temp = self.get_labels_and_classes()
        if casefold(item, format='triple') in temp.keys():
            # If this is in the ontology already as a label, create sensor triples directly
            text = ' I know about %s. It is of type %s. I will remember this object' % (item, temp[item])
            return item, text

        # Query the display for information
        class_type, description = self.exact_match_dbpedia(item)
        if class_type is not None:
            # Had to learn it, but I can create triples now
            text = ' I did not know what %s is, but I searched on the display and I found that it is a %s. ' \
                   'I will remember this object' % (item, class_type)
            return casefold(class_type, format='triple'), text

        if not exact_only:
            # Second go at dbpedia, relaxed approach
            class_type, description = self.keyword_match_dbpedia(item)
            if class_type is not None:
                # Had to really search for it to learn it, but I can create triples now
                text = ' I did not know what %s is, but I searched for fuzzy matches on the display and I found that it ' \
                       'is a %s. I will remember this object' % (item, class_type)
                return casefold(class_type, format='triple'), text

        # Failure, nothing found
        text = ' I am sorry, I could not learn anything on %s so I will not remember it' % item
        return None, text

    ########## conflicts ##########
    def _fill_entity_(self, label, namespace='LW'):
        """
        Create an RDF entity given its label and its namespace
        Parameters
        ----------
        label: str
            Label of entity
        namespace:
            Namespace where entity belongs to

        Returns
        -------
            Entity object with given label
        """
        types = self.get_type_of_instance(label)

        return Entity(self.namespaces[namespace]+label, label, types)

    def _fill_predicate_(self, label, namespace='N2MU'):
        """
        Create an RDF predicate given its label and its namespace
        Parameters
        ----------
        label: str
            Label of predicate
        namespace:
            Namespace where predicate belongs to

        Returns
        -------
            Predicate object with given label
        """

        return Predicate(self.namespaces[namespace]+label, label)

    def _fill_provenance_(self, response_item):
        """
        Structure provenance to pair authors and dates when mentions are created
        Parameters
        ----------
        response_item: dict
            standard row result from SPARQL

        Returns
        -------
            Provenance object containing author and date
        """
        author = response_item['authorlabel']['value']
        date = date_from_uri(response_item['date']['value'])

        return Provenance(author, date)

    def _fill_cardinality_conflict_(self, raw_conflict):
        """
        Structure cardinality conflict to pair provenance and object that creates the conflict
        Parameters
        ----------
        raw_conflict: dict
            standard row result from SPARQL

        Returns
        -------
            CardinalityConflict object containing provenance and entity
        """
        processed_provenance = self._fill_provenance_(raw_conflict)
        processed_entity = self._fill_entity_(raw_conflict['objectlabel']['value'])

        return CardinalityConflict(processed_provenance, processed_entity)

    def _fill_negation_conflict_(self, raw_conflict):
        """
        Structure negation conflict to pair provenance and predicate that creates the conflict
        Parameters
        ----------
        raw_conflict: dict
            standard row result from SPARQL

        Returns
        -------
            NegationConflict object containing provenance and predicate
        """
        processed_provenance = self._fill_provenance_(raw_conflict)
        processed_predicate = self._fill_predicate_(raw_conflict['pred']['value'].split('/')[-1])

        return NegationConflict(processed_provenance, processed_predicate)

    def get_all_conflicts(self):
        """
        Aggregate all conflicts in brain
        :return:
        """
        conflicts = []
        for predicate in self._ONE_TO_ONE_PREDICATES:
            conflicts.extend(self.get_conflicts_with_one_to_one_predicate(predicate))

        return conflicts

    def get_conflicts_with_one_to_one_predicate(self, one_to_one_predicate):
        query = read_query('one_to_one_conflicts') % one_to_one_predicate

        response = self._submit_query(query)
        conflicts = []
        for item in response:
            conflict = {'subject': item['sname']['value'], 'predicate': one_to_one_predicate, 'objects': []}

            for x in item['pairs']['value'].split(';'):
                [val, auth] = x.split(',')
                option = {'value': val, 'author': auth}
                conflict['objects'].append(option)

            conflicts.append(conflict)

        return conflicts

    def get_object_cardinality_conflicts_with_statement(self, capsule):
        """
        Query and build cardinality conflicts, meaning conflicts because predicates should be one to one but have
        multiple object values
        Parameters
        ----------
        capsule

        Returns
        -------
        conflicts: List[CardinalityConflicts]
            List of Conflicts containing the object which creates the conflict, and their provenance
        """
        # Case fold
        capsule = casefold_capsule(capsule, format='triple')

        if capsule['predicate']['type'] not in self._ONE_TO_ONE_PREDICATES:
            return [{}]

        query = read_query('thoughts/object_cardinality_conflicts') % (capsule['predicate']['type'],
                                                                        capsule['subject']['label'],
                                                                        capsule['object']['label'])

        response = self._submit_query(query)
        if response[0] != {}:
            conflicts = [self._fill_cardinality_conflict_(elem) for elem in response]

        return conflicts

    def get_negation_conflicts_with_statement(self, capsule):
        """
        Query and build negation conflicts, meaning conflicts because predicates are directly negated
        Parameters
        ----------
        capsule

        Returns
        -------
        conflicts: List[NegationConflict]
            List of Conflicts containing the predicate which creates the conflict, and their provenance
        """
        # Case fold
        capsule = casefold_capsule(capsule, format='triple')
        predicate = capsule['predicate']['type']
        predicate = predicate[:-4] if predicate.endswith('-not') else predicate

        query = read_query('thoughts/negation_conflicts') % (capsule['subject']['label'], capsule['object']['label'],
                                                              predicate, predicate)

        response = self._submit_query(query)
        if response[0] != {}:
            conflicts = [self._fill_negation_conflict_(elem) for elem in response]

        return conflicts

    ########## overlaps ##########
    def _fill_statement_novelty_(self, raw_conflict):
        """
        Structure statement novelty to get provenance if this statement has been heard before
        Parameters
        ----------
        raw_conflict: dict
            standard row result from SPARQL

        Returns
        -------
            StatementNovelty object containing provenance
        """
        processed_provenance = self._fill_provenance_(raw_conflict)

        return StatementNovelty(processed_provenance)

    def _fill_entity_novelty_(self, subject_url, object_url):
        """
        Structure entity novelty to signal if these entities have been heard before
        Parameters
        ----------
        subject_url: str
            URI of instance
        object_url: str
            URI of instance

        Returns
        -------
            Entity object containing boolean values signaling if they are new
        """
        subject_novelty = self.check_instance_novelty(subject_url)
        object_novelty = self.check_instance_novelty(object_url)

        return EntityNovelty(subject_novelty, object_novelty)

    def get_statement_novelty(self, statement_uri):
        """
        Query and build provenance if an instance (statement) has been learned before
        Parameters
        ----------
        statement_uri: str
            URI of instance

        Returns
        -------
        conflicts: List[StatementNovelty]
            List of provenance for the instance
        """
        query = read_query('thoughts/statement_novelty') % statement_uri
        response = self._submit_query(query)

        if response[0] != {}:
            response = [self._fill_statement_novelty_(elem) for elem in response]

        return response

    def check_instance_novelty(self, instance_url):
        """
        Query if an instance (entity) has been heard about before
        Parameters
        ----------
        instance_url: str
            URI of instance

        Returns
        -------
        conflicts: List[StatementNovelty]
            List of provenance for the instance
        """
        query = read_query('thoughts/entity_novelty') % instance_url
        response = self._submit_query(query, ask=True)

        return response


    ########## gaps ##########
    def get_gaps_from_entity(self, entity):
        # Role as subject
        query = read_query('subject_gaps') % (entity['label'], entity['label'])
        response = self._submit_query(query)

        if response:
            subject_gaps = [{'predicate': elem['p']['value'].split('/')[-1],
                            'range': elem['type2']['value'].split('/')[-1]} for elem in response
                            if elem['p']['value'].split('/')[-1] not in self._NOT_TO_ASK_PREDICATES]
        else:
            subject_gaps = []

        # Role as object
        query = read_query('object_gaps') % (entity['label'], entity['label'])
        response = self._submit_query(query)

        if response:
            object_gaps = [{'predicate': elem['p']['value'].split('/')[-1],
                            'domain': elem['type2']['value'].split('/')[-1]} for elem in response
                           if elem['p']['value'].split('/')[-1] not in self._NOT_TO_ASK_PREDICATES]
        else:
            object_gaps = []

        return {'subject': subject_gaps, 'object': object_gaps}

    ########## overlaps ##########
    def get_overlaps(self, capsule):
        # Role as subject
        query = read_query('object_overlap') % (capsule['predicate']['type'], capsule['object']['label'],
                                                capsule['subject']['label'])
        response = self._submit_query(query)

        if response:
            object_overlap = [{'subject': elem['slabel']['value'], 'author': elem['authorlabel']['value'],
                                  'date': elem['date']['value'].split('/')[-1]} for elem in response]
        else:
            object_overlap = []

        # Role as object
        query = read_query('subject_overlap') % (capsule['predicate']['type'], capsule['subject']['label'],
                                                capsule['object']['label'])
        response = self._submit_query(query)

        if response:
            subject_overlap = [{'object': elem['olabel']['value'], 'author': elem['authorlabel']['value'],
                                  'date': elem['date']['value'].split('/')[-1]} for elem in response]
        else:
            subject_overlap = []

        return {'subject': subject_overlap, 'object': object_overlap}

    ########## semantic display ##########
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

    ######################################## Helpers for statement processing ########################################

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
        if type == 'Statement':
            graph_to_write = 'Interactions'
        elif type == 'Experience':
            graph_to_write = 'Sensors'

        interaction_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + graph_to_write))
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

        interaction_graph.add((actor, RDFS.label, actor_label))
        interaction_graph.add((actor, RDF.type, actor_type1))
        interaction_graph.add((actor, RDF.type, actor_type2))
        interaction_graph.add((actor, RDF.type, actor_type3))

        # Add leolani knows/senses actor
        if type == 'Statement':
            predicate = 'knows'
        elif type == 'Experience':
            predicate = 'senses'

        interaction_graph.add((leolani, self.namespaces['N2MU'][predicate], actor))
        _, _ = self._create_claim_graph(leolani, 'leolani', actor, actor_label, predicate, type)

        # Event and subevent
        event_id = capsule['chat']
        if type == 'Statement':
            event_label = 'chat%s' % event_id
        elif type == 'Experience':
            event_label = 'visual%s' % event_id

        subevent_id = capsule['turn']
        if type == 'Statement':
            subevent_label = event_label + '_turn%s' % subevent_id
        elif type == 'Experience':
            subevent_label = event_label + '_object%s' % subevent_id

        turn = URIRef(to_iri(self.namespaces['LTa'] + subevent_label))
        turn_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        if type == 'Statement':
            turn_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Turn'))
        elif type == 'Experience':
            turn_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Object'))

        interaction_graph.add((turn, RDF.type, turn_type1))
        interaction_graph.add((turn, RDF.type, turn_type2))
        interaction_graph.add((turn, self.namespaces['N2MU']['id'], Literal(subevent_id)))
        interaction_graph.add((turn, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((turn, self.namespaces['SEM']['hasTime'], time))

        chat = URIRef(to_iri(self.namespaces['LTa'] + event_label))
        chat_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        if type == 'Statement':
            chat_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Chat'))
        elif type == 'Experience':
            chat_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Visual'))

        interaction_graph.add((chat, RDF.type, chat_type1))
        interaction_graph.add((chat, RDF.type, chat_type2))
        interaction_graph.add((chat, self.namespaces['N2MU']['id'], Literal(event_id)))
        interaction_graph.add((chat, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((chat, self.namespaces['SEM']['hasTime'], time))
        interaction_graph.add((chat, self.namespaces['SEM']['hasSubevent'], turn))

        perspective_graph, mention, attribution = self._create_perspective_graph(capsule, subevent_label)

        # Link interactions and perspectives
        perspective_graph.add((mention, self.namespaces['GRASP']['wasAttributedTo'], actor))
        perspective_graph.add((mention, self.namespaces['GRASP']['hasAttribution'], attribution))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], chat))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], turn))

        return interaction_graph, perspective_graph, actor, time, mention, attribution

    def _create_perspective_graph(self, capsule, turn_label, type='Statement'):
        # Perspective graph
        perspective_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Perspectives'))
        perspective_graph = self.dataset.graph(perspective_graph_uri)

        # Mention
        if type == 'Statement':
            mention_id = turn_label + '_char%s' % capsule['position']
        elif type == 'Experience':
            mention_id = turn_label + '_pixel%s' % capsule['position']
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

    def _model_graphs_(self, capsule, type='Statement'):
        # Leolani world (includes instance and claim graphs)
        instance_graph, claim_graph, subject, object, instance = self._create_leolani_world(capsule, type)

        # Identity
        leolani = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri

        # Leolani talk (includes interaction and perspective graphs)
        interaction_graph, perspective_graph, actor, time, mention, attribution = self._create_leolani_talk(capsule, leolani, type)

        # Interconnections
        instance_graph.add((subject, self.namespaces['GRASP']['denotedIn'], mention))
        instance_graph.add((object, self.namespaces['GRASP']['denotedIn'], mention))

        instance_graph.add((instance, self.namespaces['GRASP']['denotedBy'], mention))
        instance_graph.add((instance, self.namespaces['SEM']['hasActor'], actor))
        instance_graph.add((instance, self.namespaces['SEM']['hasTime'], time))

        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], subject))
        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], object))
        perspective_graph.add((mention, self.namespaces['GRASP']['denotes'], instance))

        perspective_graph.add((attribution, self.namespaces['GRASP']['isAttributionFor'], mention))

        return subject, object, instance

    ######################################### Helpers for question processing #########################################

    def _create_query(self, parsed_question):
        _ = hash_statement_id([parsed_question['subject']['label'], parsed_question['predicate']['type'], parsed_question['object']['label']])

        # Query subject
        if parsed_question['subject']['label'] == "":
            # Case fold
            # object_label = casefold_label(parsed_question['object']['label'], format='triple')

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

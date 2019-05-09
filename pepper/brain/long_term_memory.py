from pepper.brain.utils.response import CardinalityConflict, NegationConflict, StatementNovelty, EntityNovelty, \
    Gap, Gaps, Overlap, Overlaps, Thoughts
from pepper.brain.utils.helper_functions import hash_claim_id, read_query, casefold_text
from pepper.brain.utils.constants import NAMESPACE_MAPPING
from pepper.brain.basic_brain import BasicBrain
from pepper.language.utils.atoms import UtteranceType

from pepper import config

from rdflib import RDF, RDFS, OWL
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

        self.myself = None  # NOT USED, ONLY WHEN UPLOADING/EXPERIENCING
        self.query_prefixes = read_query('prefixes')  # NOT USED, ONLY WHEN QUERYING

        # Launch first query
        self.count_statements()

    #################################### Main functions to interact with the brain ####################################

    def update(self, utterance):
        # type (Utterance) -> Thoughts
        """
        Main function to interact with if a statement is coming into the brain. Takes in an Utterance containing a
        parsed statement as a Triple, transforms them to linked data, and posts them to the triple store
        Parameters
        ----------
        utterance: Utterance
            Contains all necessary information regarding a statement just made.

        Returns
        -------
        thoughts: Thoughts
            Contains information about conflicts, novelty, gaps and overlaps that the statement produces given the data
            in the triple store

        """
        if utterance.triple is not None:

            # Casefold
            utterance.casefold(format='triple')

            # Create graphs and triples
            instance = self._model_graphs_(utterance)

            # Check if this knowledge already exists on the brain
            statement_novelty = self.get_statement_novelty(instance.id)

            # Check how many items of the same type as subject and object we have
            entity_novelty = self._fill_entity_novelty_(utterance.triple.subject.id, utterance.triple.object.id)

            # Find any overlaps
            overlaps = self.get_overlaps(utterance)

            # Finish process of uploading new knowledge to the triple store
            data = self._serialize(self._brain_log)
            code = self._upload_to_brain(data)

            # Check for conflicts after adding the knowledge
            negation_conflicts = self.get_negation_conflicts(utterance)
            object_conflict = self.get_object_cardinality_conflicts(utterance)

            # Check for gaps, in case we want to be proactive
            subject_gaps = self.get_entity_gaps(utterance.triple.subject)
            object_gaps = self.get_entity_gaps(utterance.triple.object)

            # Report trust
            trust = 0 if self.when_last_chat_with(utterance.chat_speaker) == '' else 1

            # Create JSON output
            thoughts = Thoughts(statement_novelty, entity_novelty, negation_conflicts, object_conflict,
                                subject_gaps, object_gaps, overlaps, trust)
            output = {'response': code, 'statement': utterance, 'thoughts': thoughts}

        else:
            # Create JSON output
            output = {'response': None, 'statement': utterance, 'thoughts': None}

        return output

    def experience(self, utterance):
        """
        Main function to interact with if an experience is coming into the brain. Takes in a structured utterance
        containing parsed experience, transforms them to triples, and posts them to the triple store
        :param utterance: Structured data of a parsed experience
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Create graphs and triples
        instance = self._model_graphs_(utterance)
        data = self._serialize(self._brain_log)
        code = self._upload_to_brain(data)

        # Create JSON output
        output = {'response': code, 'statement': utterance}

        return output

    def query_brain(self, utterance):
        """
        Main function to interact with if a question is coming into the brain. Takes in a structured parsed question,
        transforms it into a query, and queries the triple store for a response
        :param utterance: Structured data of a parsed question
        :return: json response containing the results of the query, and the original question
        """

        # Generate query
        query = self._create_query(utterance)

        # Perform query
        response = self._submit_query(query)

        # Create JSON output
        output = {'response': response, 'question': utterance}

        return output

    def process_visual(self, item, exact_only=True):
        """
        Main function to determine if this item can be recognized by the brain, learned, or none
        :param item:
        :return:
        """

        if casefold_text(item, format='triple') in self.get_classes():
            # If this is in the ontology already as a class, create sensor triples directly
            text = 'I know about %s. I will remember this object' % item
            return item, text

        temp = self.get_labels_and_classes()
        if casefold_text(item, format='triple') in temp.keys():
            # If this is in the ontology already as a label, create sensor triples directly
            text = ' I know about %s. It is of type %s. I will remember this object' % (item, temp[item])
            return item, text

        # Query the display for information
        class_type, description = self.exact_match_dbpedia(item)
        if class_type is not None:
            # Had to learn it, but I can create triples now
            text = ' I did not know what %s is, but I searched on the display and I found that it is a %s. ' \
                   'I will remember this object' % (item, class_type)
            return casefold_text(class_type, format='triple'), text

        if not exact_only:
            # Second go at dbpedia, relaxed approach
            class_type, description = self.keyword_match_dbpedia(item)
            if class_type is not None:
                # Had to really search for it to learn it, but I can create triples now
                text = ' I did not know what %s is, but I searched for fuzzy matches on the display and I found that it ' \
                       'is a %s. I will remember this object' % (item, class_type)
                return casefold_text(class_type, format='triple'), text

        # Failure, nothing found
        text = ' I am sorry, I could not learn anything on %s so I will not remember it' % item
        return None, text

    ########## conflicts ##########
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
        processed_provenance = self._rdf_builder.fill_provenance(raw_conflict['authorlabel']['value'],
                                                                 raw_conflict['date']['value'])
        processed_type = self.get_type_of_instance(raw_conflict['objectlabel']['value'])
        processed_entity = self._rdf_builder.fill_entity(raw_conflict['objectlabel']['value'], processed_type)

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
        preprocessed_date = self._rdf_builder.label_from_uri(raw_conflict['date']['value'], 'LC')
        processed_provenance = self._rdf_builder.fill_provenance(raw_conflict['authorlabel']['value'],
                                                                 preprocessed_date)
        processed_predicate = self._rdf_builder.fill_predicate(raw_conflict['pred']['value'].split('/')[-1])

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

    def get_object_cardinality_conflicts(self, utterance):
        """
        Query and build cardinality conflicts, meaning conflicts because predicates should be one to one but have
        multiple object values
        Parameters
        ----------
        utterance

        Returns
        -------
        conflicts: List[CardinalityConflicts]
            List of Conflicts containing the object which creates the conflict, and their provenance
        """
        if utterance.triple.predicate_name not in self._ONE_TO_ONE_PREDICATES:
            return []

        query = read_query('thoughts/object_cardinality_conflicts') % (utterance.triple.predicate_name,
                                                                       utterance.triple.subject_name,
                                                                       utterance.triple.object_name)

        response = self._submit_query(query)
        if response[0] != {}:
            conflicts = [self._fill_cardinality_conflict_(elem) for elem in response]
        else:
            conflicts = []

        return conflicts

    def get_negation_conflicts(self, utterance):
        """
        Query and build negation conflicts, meaning conflicts because predicates are directly negated
        Parameters
        ----------
        utterance

        Returns
        -------
        conflicts: List[NegationConflict]
            List of Conflicts containing the predicate which creates the conflict, and their provenance
        """
        # Case fold
        predicate = utterance.triple.predicate_name[:-4] if utterance.triple.predicate_name.endswith('-not') \
            else utterance.triple.predicate_name

        query = read_query('thoughts/negation_conflicts') % (
            utterance.triple.subject_name, utterance.triple.object_name,
            predicate, predicate)

        response = self._submit_query(query)
        if response[0] != {}:
            conflicts = [self._fill_negation_conflict_(elem) for elem in response]
        else:
            conflicts = []

        return conflicts

    ########## novelty ##########
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
        preprocessed_date = self._rdf_builder.label_from_uri(raw_conflict['date']['value'], 'LC')
        processed_provenance = self._rdf_builder.fill_provenance(raw_conflict['authorlabel']['value'],
                                                                 preprocessed_date)

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
        response: List[StatementNovelty]
            List of provenance for the instance
        """
        query = read_query('thoughts/statement_novelty') % statement_uri
        response = self._submit_query(query)

        if response[0] != {}:
            response = [self._fill_statement_novelty_(elem) for elem in response]
        else:
            response = []

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
    def _fill_entity_gap_(self, raw_conflict):
        """
        Structure entity gap to get the predicate and range of what has been learned but not heard
        Parameters
        ----------
        raw_conflict: dict
            standard row result from SPARQL

        Returns
        -------
            Gap object containing a predicate and its range
        """

        processed_predicate = self._rdf_builder.fill_predicate(raw_conflict['p']['value'].split('/')[-1])
        processed_range = self._rdf_builder.fill_entity('', namespace='N2MU',
                                                        types=[raw_conflict['type2']['value'].split('/')[-1]])

        return Gap(processed_predicate, processed_range)

    def get_entity_gaps(self, entity):
        """
        Query and build gaps with regards to the range and domain of the given entity and its predicates
        Parameters
        ----------
        entity: dict
            Information regarding the entity

        Returns
        -------
            Gaps object containing gaps related to range and domain information that could be learned
        """
        # Role as subject
        query = read_query('thoughts/subject_gaps') % (entity.label, entity.label)
        response = self._submit_query(query)

        if response:
            subject_gaps = [self._fill_entity_gap_(elem)
                            for elem in response
                            if elem['p']['value'].split('/')[-1] not in self._NOT_TO_ASK_PREDICATES]

        else:
            subject_gaps = []

        # Role as object
        query = read_query('thoughts/object_gaps') % (entity.label, entity.label)
        response = self._submit_query(query)

        if response:
            object_gaps = [self._fill_entity_gap_(elem)
                           for elem in response
                           if elem['p']['value'].split('/')[-1] not in self._NOT_TO_ASK_PREDICATES]

        else:
            object_gaps = []

        return Gaps(subject_gaps, object_gaps)

    ########## overlaps ##########
    def _fill_overlap_(self, raw_conflict):
        """
        Structure overlap to get the provenance and entity on which they overlap
        Parameters
        ----------
        raw_conflict: dict
            standard row result from SPARQL

        Returns
        -------
            Overlap object containing an entity and the provenance of the mention causing the overlap
        """
        preprocessed_date = self._rdf_builder.label_from_uri(raw_conflict['date']['value'], 'LC')
        preprocessed_types = self._rdf_builder.clean_aggregated_types(raw_conflict['types']['value'])

        processed_provenance = self._rdf_builder.fill_provenance(raw_conflict['authorlabel']['value'],
                                                                 preprocessed_date)
        processed_entity = self._rdf_builder.fill_entity(raw_conflict['label']['value'], preprocessed_types, 'LW')

        return Overlap(processed_provenance, processed_entity)

    def get_overlaps(self, utterance):
        """
        Query and build overlaps with regards to the subject and object of the heard statement
        Parameters
        ----------
        utterance

        Returns
        -------
            Overlaps containing shared information with the heard statement
        """
        # Role as subject
        query = read_query('thoughts/object_overlap') % (utterance.triple.predicate_name, utterance.triple.object_name,
                                                         utterance.triple.subject_name)
        response = self._submit_query(query)

        if response[0]['types']['value'] != '':
            object_overlap = [self._fill_overlap_(elem) for elem in response]
        else:
            object_overlap = []

        # Role as object
        query = read_query('thoughts/subject_overlap') % (
            utterance.triple.predicate_name, utterance.triple.subject_name,
            utterance.triple.object_name)
        response = self._submit_query(query)

        if response[0]['types']['value'] != '':
            subject_overlap = [self._fill_overlap_(elem) for elem in response]
        else:
            subject_overlap = []

        return Overlaps(subject_overlap, object_overlap)

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
        r = [{'label': e['label'], 'classes': e['classes'], 'description': e['description']} for e in r if
             e['label'] == best_match[0]]

        if r:
            r = r[0]

            if r['classes']:
                # process dbpedia classes only
                r['classes'] = [c['label'] for c in r['classes'] if 'dbpedia' in c['uri']]

        else:
            r = {'label': None, 'classes': None, 'description': None}

        return r['classes'][0] if r['classes'] else None, r['description'].split('.')[0] if r['description'] else None

    ######################################## Helpers for statement processing ########################################

    def _link_leolani(self):
        if self.myself is None:
            # Create Leolani
            self.myself = self._rdf_builder.fill_entity('leolani', ['robot'], 'LW')

        self._link_entity(self.myself, self.instance_graph)

    def _link_entity(self, entity, graph, namespace_mapping=None):
        # Set basics like label
        graph.add((entity.id, RDFS.label, entity.label))

        # Set types
        if entity.types == ['']:  # We only get the label
            entity_type = self._rdf_builder.create_resource_uri(OWL, 'Thing')
            graph.add((entity.id, RDF.type, entity_type))

        else:
            namespace_mapping = NAMESPACE_MAPPING \
                if namespace_mapping is None else namespace_mapping.update(NAMESPACE_MAPPING)

            for item in entity.types:
                entity_type = self._rdf_builder.create_resource_uri(namespace_mapping.get(item, 'N2MU'), item)
                graph.add((entity.id, RDF.type, entity_type))

    def _create_context(self, utterance):
        # Time
        time_label = '%s' % utterance.datetime.strftime('%Y-%m-%d')
        time = self._rdf_builder.fill_entity(time_label, ['DateTimeDescription'], 'LC')
        self._link_entity(time, self.interaction_graph)

        # Set specifics of datetime
        day = self._rdf_builder.fill_literal(utterance.datetime.day, datatype=self.namespaces['XML']['gDay'])
        month = self._rdf_builder.fill_literal(utterance.datetime.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = self._rdf_builder.fill_literal(utterance.datetime.year, datatype=self.namespaces['XML']['gYear'])
        time_unit = self._rdf_builder.create_resource_uri('TIME', 'unitDay')

        self.interaction_graph.add((time.id, self.namespaces['TIME']['day'], day))
        self.interaction_graph.add((time.id, self.namespaces['TIME']['month'], month))
        self.interaction_graph.add((time.id, self.namespaces['TIME']['year'], year))
        self.interaction_graph.add((time.id, self.namespaces['TIME']['unitType'], time_unit))

        return time

    def _create_actor(self, utterance):
        # Actor
        actor = self._rdf_builder.fill_entity(utterance.chat_speaker,
                                              ['Source', 'Actor', '%s' % ('person'
                                                                          if utterance.type == UtteranceType.STATEMENT
                                                                          else 'sensor')],
                                              'LF')
        self._link_entity(actor, self.interaction_graph)

        # Add leolani knows/senses actor
        predicate = self._rdf_builder.fill_predicate('know') if utterance.type == UtteranceType.STATEMENT \
            else self._rdf_builder.fill_predicate('sense')
        interaction = self._create_claim_graph(self.myself, predicate, actor, utterance.type)

        return actor, interaction

    def _create_events(self, utterance, actor, claim_type):
        # Chat or visual
        event_id = self._rdf_builder.fill_literal(utterance.chat.id, datatype=self.namespaces['XML']['string'])
        event_type = 'Chat' if claim_type == UtteranceType.STATEMENT else 'Visual'
        event_label = '%s%s' % (event_type, utterance.chat.id)

        # Utterance or object
        subevent_id = self._rdf_builder.fill_literal(utterance.turn, datatype=self.namespaces['XML']['string'])
        subevent_type = '%s' % ('Utterance' if claim_type == UtteranceType.STATEMENT else 'Object')
        subevent_label = '%s_%s%s' % (event_label, subevent_type, utterance.turn)

        # Add subevent
        subevent = self._rdf_builder.fill_entity(subevent_label, ['Event', subevent_type], 'LTa')
        self._link_entity(subevent, self.interaction_graph)
        self.interaction_graph.add((subevent.id, self.namespaces['N2MU']['id'], subevent_id))
        self.interaction_graph.add((subevent.id, self.namespaces['SEM']['hasActor'], actor.id))

        # Add event and link to subevent
        event = self._rdf_builder.fill_entity(event_label, ['Event', event_type], 'LTa')
        self._link_entity(event, self.interaction_graph)
        self.interaction_graph.add((event.id, self.namespaces['N2MU']['id'], event_id))
        self.interaction_graph.add((event.id, self.namespaces['SEM']['hasSubevent'], subevent.id))

        return event, subevent

    def _create_instance_graph(self, utterance):
        # type (Utterance) -> Graph, Graph, str, str, str
        """
        Create linked data related to what leolani learned/knows about the world
        Parameters
        ----------
        utterance: Utterance

        Returns
        -------


        """

        # Through object detection TODO label must be numbered to differentiate
        self._link_leolani()
        prdt = self._rdf_builder.fill_predicate('sees')
        for item in utterance.context.all_objects:
            if item.name.lower() != 'person':
                objct = self._rdf_builder.fill_entity(casefold_text(item.name, format='triple'),
                                                      [casefold_text(item.name, format='triple'), 'Detection'],
                                                      'LW')
                self._link_entity(objct, self.instance_graph)
                claim = self._create_claim_graph(self.myself, prdt, objct, UtteranceType.EXPERIENCE)

        for item in utterance.context.all_people:
            if item.name.lower() != item.UNKNOWN.lower():
                prsn = self._rdf_builder.fill_entity(casefold_text(item.name, format='triple'), ['person', 'Detection'],
                                                     'LW')
                self._link_entity(prsn, self.instance_graph)
                claim = self._create_claim_graph(self.myself, prdt, prsn, UtteranceType.EXPERIENCE)

        # Through conversation
        # Subject
        if utterance.type == UtteranceType.STATEMENT:
            utterance.triple.subject.add_types(['Instance'])
            self._link_entity(utterance.triple.subject, self.instance_graph)
        elif utterance.type == UtteranceType.EXPERIENCE:
            self._link_leolani()

        # Object
        utterance.triple.object.add_types(['Instance'])
        self._link_entity(utterance.triple.object, self.instance_graph)

        # Claim graph
        predicate = utterance.triple.predicate if utterance.type == UtteranceType.STATEMENT \
            else self._rdf_builder.fill_predicate('sees')

        claim = self._create_claim_graph(utterance.triple.subject, predicate, utterance.triple.object,
                                         utterance.type)

        return claim

    def _create_claim_graph(self, subject, predicate, object, claim_type):
        # Statement
        claim_label = hash_claim_id([subject.label, predicate.label, object.label])

        claim = self._rdf_builder.fill_entity(claim_label, ['Event', 'Instance', claim_type.name.title()], 'LW')
        self._link_entity(claim, self.claim_graph)

        # Create graph and add triple
        graph = self.dataset.graph(claim.id)
        graph.add((subject.id, predicate.id, object.id))

        return claim

    def _create_interaction_graph(self, utterance):
        # Actor
        actor, interaction = self._create_actor(utterance)

        # Event and subevent
        event, subevent = self._create_events(utterance, actor, utterance.type)

        # Add context TODO add place, detections
        time = self._create_context(utterance)
        context = self._rdf_builder.fill_entity('Context', ['Context'], 'LC')
        self._link_entity(context, self.interaction_graph)

        self.interaction_graph.add((context.id, self.namespaces['SEM']['hasBeginTimeStamp'], time.id))
        self.interaction_graph.add((context.id, self.namespaces['SEM']['hasEvent'], event.id))

        mention, attribution = self._create_perspective_graph(utterance, subevent)

        # Link interactions and perspectives
        self.perspective_graph.add((mention.id, self.namespaces['GRASP']['wasAttributedTo'], actor.id))
        self.perspective_graph.add((mention.id, self.namespaces['GRASP']['hasAttribution'], attribution.id))
        self.perspective_graph.add((mention.id, self.namespaces['PROV']['wasDerivedFrom'], event.id))
        self.perspective_graph.add((mention.id, self.namespaces['PROV']['wasDerivedFrom'], subevent.id))

        return interaction, mention, attribution

    def _create_perspective_graph(self, utterance, subevent):
        # Mention
        mention_unit = 'Char' if utterance.type == UtteranceType.STATEMENT else 'Pixel'
        mention_position = '0-%s' % len(utterance.transcript)
        mention_label = '%s%s%s' % (subevent.label, mention_unit, mention_position)

        mention = self._rdf_builder.fill_entity(mention_label, ['Mention'], 'LTa')
        self._link_entity(mention, self.perspective_graph)

        # Attribution
        attribution_label = mention_label + '_CERTAIN'
        attribution_value = self._rdf_builder.create_resource_uri('GRASP', 'CERTAIN')

        attribution = self._rdf_builder.fill_entity(attribution_label, ['Attribution'], 'LTa')
        self._link_entity(attribution, self.perspective_graph)

        self.perspective_graph.add((attribution.id, RDF.value, attribution_value))

        return mention, attribution

    def _serialize(self, file_path):
        """
        Save graph to local file and return the serialized string
        :param file_path: path to where data will be saved
        :return: serialized data as string
        """
        # Save to file but return the python representation
        with open(file_path + '.' + self._connection.format, 'w') as f:
            self.dataset.serialize(f, format=self._connection.format)
        return self.dataset.serialize(format=self._connection.format)

    def _model_graphs_(self, utterance):
        # Leolani world (includes instance and claim graphs)
        instance = self._create_instance_graph(utterance)

        # Leolani talk (includes interaction and perspective graphs)
        interaction, mention, attribution = self._create_interaction_graph(utterance)

        # Interconnections
        self.instance_graph.add((utterance.triple.subject.id, self.namespaces['GRASP']['denotedIn'], mention.id))
        self.instance_graph.add((utterance.triple.object.id, self.namespaces['GRASP']['denotedIn'], mention.id))

        self.claim_graph.add((instance.id, self.namespaces['GRASP']['denotedBy'], mention.id))
        self.claim_graph.add((interaction.id, self.namespaces['GRASP']['denotedBy'], mention.id))

        self.perspective_graph.add(
            (mention.id, self.namespaces['GRASP']['containsDenotation'], utterance.triple.subject.id))
        self.perspective_graph.add(
            (mention.id, self.namespaces['GRASP']['containsDenotation'], utterance.triple.object.id))
        self.perspective_graph.add((mention.id, self.namespaces['GRASP']['denotes'], instance.id))

        self.perspective_graph.add((attribution.id, self.namespaces['GRASP']['isAttributionFor'], mention.id))

        return instance

    ######################################### Helpers for question processing #########################################

    def _create_query(self, utterance):
        empty = self._rdf_builder.fill_literal('')

        # Query subject
        if utterance.triple.subject_name == empty:
            query = """
                SELECT distinct ?slabel ?authorlabel
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
                """ % (utterance.triple.predicate_name,
                       utterance.triple.object_name,
                       utterance.triple.predicate_name)

        # Query object
        elif utterance.triple.object_name == empty:
            query = """
                SELECT distinct ?olabel ?authorlabel
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
                """ % (utterance.triple.predicate_name,
                       utterance.triple.subject_name,
                       utterance.triple.predicate_name)

        # Query existence
        else:
            query = """
                SELECT distinct ?authorlabel ?v
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
                """ % (utterance.triple.predicate_name,
                       utterance.triple.subject_name,
                       utterance.triple.object_name,
                       utterance.triple.predicate_name)

        query = self.query_prefixes + query

        return query

from pepper.brain.utils.helper_functions import hash_claim_id, read_query, casefold_text, \
    confidence_to_certainty_value, polarity_to_polarity_value, sentiment_to_sentiment_value, get_object_id
from pepper.brain.utils.location_reasoner import LocationReasoner
from pepper.brain.utils.thought_generator import ThoughtGenerator
from pepper.brain.utils.type_reasoner import TypeReasoner
from pepper.brain.utils.constants import NAMESPACE_MAPPING
from pepper.brain.utils.response import Thoughts
from pepper.brain.basic_brain import BasicBrain

from pepper.language.utils.atoms import UtteranceType

from pepper import config

from rdflib import RDF, RDFS, OWL


class LongTermMemory(BasicBrain):
    def __init__(self, address=config.BRAIN_URL_LOCAL, clear_all=False):
        # type: (str, bool) -> LongTermMemory
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        super(LongTermMemory, self).__init__(address, clear_all)

        self.myself = None
        self.query_prefixes = read_query('prefixes')  # USED ONLY WHEN QUERYING
        self.thought_generator = ThoughtGenerator()
        self.location_reasoner = LocationReasoner()
        self.type_reasoner = TypeReasoner()

        self.set_location_label = self.location_reasoner.set_location_label
        self.reason_location = self.location_reasoner.reason_location

    #################################### Main functions to interact with the brain ####################################
    def get_thoughts_on_entity(self, entity_label, reason_types=False):
        if entity_label is not None and entity_label != '':
            # Casefold
            entity_label = casefold_text(entity_label, format='triple')
            entity_type = None

            if reason_types:
                # Try to figure out what this entity is
                entity_type, _ = self.type_reasoner.reason_entity_type(entity_label, exact_only=True)

            if entity_type is not None:
                entity = self._rdf_builder.fill_entity(entity_label, entity_type, 'LW')
            else:
                entity = self._rdf_builder.fill_entity_from_label(entity_label, 'N2MU')

            triple = self._rdf_builder.fill_triple_from_label('leolani', 'see', entity_label)

            # Check how many items of the same type as subject and complement we have
            entity_novelty = self.thought_generator.fill_entity_novelty(entity.id, entity.id)

            # Check for gaps, in case we want to be proactive
            entity_gaps = self.thought_generator.get_entity_gaps(entity)

            # Create JSON output
            thoughts = Thoughts([], entity_novelty, [], [], entity_gaps, entity_gaps, [], None)
            output = {'response': 200, 'entity': entity, 'thoughts': thoughts}

        else:
            # Create JSON output
            output = {'response': None, 'entity': None, 'thoughts': None}

        return output

    def update(self, utterance, reason_types=False):
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

            if reason_types:
                # Try to figure out what this entity is
                if not utterance.triple.complement.types:
                    complement_type, _ = self.type_reasoner.reason_entity_type(str(utterance.triple.complement_name),
                                                                           exact_only=True)
                    utterance.triple.complement.add_types([complement_type])

                if not utterance.triple.subject.types:
                    subject_type, _ = self.type_reasoner.reason_entity_type(str(utterance.triple.subject_name),
                                                                            exact_only=True)
                    utterance.triple.complement.add_types([subject_type])

            # Create graphs and triples
            instance = self._model_graphs_(utterance)

            # Check if this knowledge already exists on the brain
            statement_novelty = self.thought_generator.get_statement_novelty(instance.id)

            # Check how many items of the same type as subject and complement we have
            entity_novelty = self.thought_generator.fill_entity_novelty(utterance.triple.subject.id,
                                                                        utterance.triple.complement.id)

            # Find any overlaps
            overlaps = self.thought_generator.get_overlaps(utterance)

            # Finish process of uploading new knowledge to the triple store
            data = self._serialize(self._brain_log)
            code = self._upload_to_brain(data)

            # Check for conflicts after adding the knowledge
            negation_conflicts = self.thought_generator.get_negation_conflicts(utterance)
            complement_conflict = self.thought_generator.get_complement_cardinality_conflicts(utterance)

            # Check for gaps, in case we want to be proactive
            subject_gaps = self.thought_generator.get_entity_gaps(utterance.triple.subject,
                                                                  exclude=utterance.triple.complement)
            complement_gaps = self.thought_generator.get_entity_gaps(utterance.triple.complement,
                                                                 exclude=utterance.triple.subject)

            # Report trust
            trust = 0 if self.when_last_chat_with(utterance.chat_speaker) == '' else 1

            # Create JSON output
            thoughts = Thoughts(statement_novelty, entity_novelty, negation_conflicts, complement_conflict,
                                subject_gaps, complement_gaps, overlaps, trust)
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
        _ = self._model_graphs_(utterance)
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
        self._log.info("Triple: {}".format(utterance.triple))

        # Perform query
        response = self._submit_query(query)

        # Create JSON output
        output = {'response': response, 'question': utterance}

        return output

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

    def _create_detections(self, cntxt, context):
        # Get ids of existing objects in this location
        memory = self.location_reasoner.get_location_memory(cntxt)

        # Detections: objects
        self._link_leolani()
        prdt = self._rdf_builder.fill_predicate('see')
        object_type = self._rdf_builder.create_resource_uri('N2MU', 'object')
        instances = []
        observations = []

        for item in cntxt.objects:
            if item.name.lower() != 'person':
                # Create instance and link detection to graph
                mem_id, memory = get_object_id(memory, item.name)
                objct_id = self._rdf_builder.fill_literal(mem_id, datatype=self.namespaces['XML']['string'])
                objct = self._rdf_builder.fill_entity(casefold_text('%s %s' % (item.name, objct_id), format='triple'),
                                                      [casefold_text(item.name, format='triple'), 'Instance',
                                                       'object'],
                                                      'LW')
                self._link_entity(objct, self.instance_graph)
                self.interaction_graph.add((objct.id, self.namespaces['N2MU']['id'], objct_id))
                instances.append(objct)
                # Bidirectional link to context
                self.interaction_graph.add((context.id, self.namespaces['EPS']['hasDetection'], objct.id))
                self.instance_graph.add((objct.id, self.namespaces['EPS']['hasContext'], context.id))
                # Create detection
                objct_detection = self._create_claim_graph(self.myself, prdt, objct, UtteranceType.EXPERIENCE)
                self.claim_graph.add((objct_detection.id, self.namespaces['EPS']['hasContext'], context.id))

                observations.append(objct_detection)

                # Open ended learning
                learnable_type = self._rdf_builder.create_resource_uri('N2MU',
                                                                       casefold_text(item.name, format='triple'))
                self.ontology_graph.add((learnable_type, RDFS.subClassOf, object_type))

        # Detections: faces
        for item in cntxt.people:
            if item.name.lower() != item.UNKNOWN.lower():
                # Create and link detection to instance graph
                prsn = self._rdf_builder.fill_entity(casefold_text(item.name, format='triple'), ['person', 'Instance'],
                                                     'LW')
                instances.append(prsn)
                self._link_entity(prsn, self.instance_graph)
                # Bidirectional link to context
                self.interaction_graph.add((context.id, self.namespaces['EPS']['hasDetection'], prsn.id))
                self.instance_graph.add((prsn.id, self.namespaces['EPS']['hasContext'], context.id))
                # Create detection
                face_detection = self._create_claim_graph(self.myself, prdt, prsn, UtteranceType.EXPERIENCE)
                self.claim_graph.add((face_detection.id, self.namespaces['EPS']['hasContext'], context.id))
                observations.append(face_detection)

        return instances, observations

    def create_context(self, cntxt):
        # Create an episodic awareness by making a context
        context_id = self._rdf_builder.fill_literal(cntxt.id, datatype=self.namespaces['XML']['string'])
        context = self._rdf_builder.fill_entity('context%s' % cntxt.id, ['Context'], 'LC')
        self._link_entity(context, self.interaction_graph)
        self.interaction_graph.add((context.id, self.namespaces['N2MU']['id'], context_id))

        # Time
        time = self._rdf_builder.fill_entity(cntxt.datetime.strftime('%Y-%m-%d'), ['Time', 'DateTimeDescription'], 'LC')
        self._link_entity(time, self.interaction_graph)
        self.interaction_graph.add((context.id, self.namespaces['SEM']['hasBeginTimeStamp'], time.id))

        # Set specifics of datetime
        day = self._rdf_builder.fill_literal(cntxt.datetime.day, datatype=self.namespaces['XML']['gDay'])
        month = self._rdf_builder.fill_literal(cntxt.datetime.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = self._rdf_builder.fill_literal(cntxt.datetime.year, datatype=self.namespaces['XML']['gYear'])
        time_unit = self._rdf_builder.create_resource_uri('TIME', 'unitDay')
        self.interaction_graph.add((time.id, self.namespaces['TIME']['day'], day))
        self.interaction_graph.add((time.id, self.namespaces['TIME']['month'], month))
        self.interaction_graph.add((time.id, self.namespaces['TIME']['year'], year))
        self.interaction_graph.add((time.id, self.namespaces['TIME']['unitType'], time_unit))

        # Place

        if cntxt.location is not None:
            location_id = self._rdf_builder.fill_literal(cntxt.location.id, datatype=self.namespaces['XML']['string'])
            location_city = self._rdf_builder.fill_entity(cntxt.location.city, ['location', 'city', 'Place'], 'LW')
            self._link_entity(location_city, self.interaction_graph)
            location_country = self._rdf_builder.fill_entity(cntxt.location.country, ['location', 'country', 'Place'],
                                                             'LW')
            self._link_entity(location_country, self.interaction_graph)
            location_region = self._rdf_builder.fill_entity(cntxt.location.region, ['location', 'region', 'Place'],
                                                            'LW')
            self._link_entity(location_region, self.interaction_graph)
            location = self._rdf_builder.fill_entity(cntxt.location.label, ['location', 'Place'], 'LC')
            self._link_entity(location, self.interaction_graph)
            self.interaction_graph.add((location.id, self.namespaces['N2MU']['id'], location_id))
            self.interaction_graph.add((location.id, self.namespaces['N2MU']['in'], location_city.id))
            self.interaction_graph.add((location.id, self.namespaces['N2MU']['in'], location_country.id))
            self.interaction_graph.add((location.id, self.namespaces['N2MU']['in'], location_region.id))
            self.interaction_graph.add((context.id, self.namespaces['SEM']['hasPlace'], location.id))

        # Detections
        instances, observations = self._create_detections(cntxt, context)

        return context, instances, observations

    def _create_actor(self, utterance, claim_type):
        # Actor
        actor = self._rdf_builder.fill_entity('%s' % (utterance.chat_speaker
                                                      if claim_type == UtteranceType.STATEMENT
                                                      else 'front-camera'),
                                              ['Instance', 'Source',
                                               'Actor', '%s' % ('person'
                                                                if claim_type == UtteranceType.STATEMENT
                                                                else 'sensor')],
                                              '%s' % ('LF'
                                                      if claim_type == UtteranceType.STATEMENT
                                                      else 'LI'))
        self._link_entity(actor, self.interaction_graph)

        # Add leolani knows/senses actor
        predicate = self._rdf_builder.fill_predicate('know') if claim_type == UtteranceType.STATEMENT \
            else self._rdf_builder.fill_predicate('sense')
        interaction = self._create_claim_graph(self.myself, predicate, actor, claim_type)

        return actor, interaction

    def _create_events(self, utterance, claim_type, context):
        # Chat or Visual
        event_id = self._rdf_builder.fill_literal(utterance.chat.id, datatype=self.namespaces['XML']['string'])
        event_type = '%s' % ('chat' if claim_type == UtteranceType.STATEMENT else 'visual')
        eventt_label = '%s%s' % (event_type, str(event_id))
        event = self._rdf_builder.fill_entity(eventt_label, ['Event', '%s' % event_type.title()], 'LTa')
        self._link_entity(event, self.interaction_graph)
        self.interaction_graph.add((event.id, self.namespaces['N2MU']['id'], event_id))
        self.interaction_graph.add((context.id, self.namespaces['SEM']['hasEvent'], event.id))

        # Utterance or Visual are events and instances
        subevent_id = self._rdf_builder.fill_literal(utterance.turn, datatype=self.namespaces['XML']['string'])
        subevent_type = '%s' % ('utterance' if claim_type == UtteranceType.STATEMENT else 'detection')
        subevent_label = '%s_%s%s' % (str(event.label), subevent_type, str(subevent_id))
        subevent = self._rdf_builder.fill_entity(subevent_label, ['Event', '%s' % subevent_type.title()], 'LTa')
        self._link_entity(subevent, self.interaction_graph)

        # Actor
        actor, interaction = self._create_actor(utterance, claim_type)
        self.interaction_graph.add((subevent.id, self.namespaces['N2MU']['id'], subevent_id))
        self.interaction_graph.add((subevent.id, self.namespaces['SEM']['hasActor'], actor.id))
        self.interaction_graph.add((event.id, self.namespaces['SEM']['hasSubEvent'], subevent.id))

        return subevent, actor, interaction

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
        self._link_leolani()
        # Subject
        if utterance.type == UtteranceType.STATEMENT:
            utterance.triple.subject.add_types(['Instance'])
            self._link_entity(utterance.triple.subject, self.instance_graph)
        elif utterance.type == UtteranceType.EXPERIENCE:
            self._link_leolani()

        # Complement
        utterance.triple.complement.add_types(['Instance'])
        self._link_entity(utterance.triple.complement, self.instance_graph)

        # Claim graph
        predicate = utterance.triple.predicate if utterance.type == UtteranceType.STATEMENT \
            else self._rdf_builder.fill_predicate('see')

        claim = self._create_claim_graph(utterance.triple.subject, predicate, utterance.triple.complement,
                                         utterance.type)

        return claim

    def _create_claim_graph(self, subject, predicate, complement, claim_type=UtteranceType.STATEMENT):
        # Statement
        claim_label = hash_claim_id([subject.label, predicate.label, complement.label])

        claim = self._rdf_builder.fill_entity(claim_label, ['Event', 'Instance', claim_type.name.title()], 'LW')
        self._link_entity(claim, self.claim_graph)

        # Create graph and add triple
        graph = self.dataset.graph(claim.id)
        graph.add((subject.id, predicate.id, complement.id))

        return claim

    def _create_interaction_graph(self, utterance, claim):
        # Add context
        context, detections, observations = self.create_context(utterance.context)

        # Subevents
        experience, sensor, use_sensor = self._create_events(utterance, UtteranceType.EXPERIENCE, context)
        for detection, observation in zip(detections, observations):
            mention, attribution = self._create_perspective_graph(utterance, experience, UtteranceType.EXPERIENCE,
                                                                  detection=detection)
            self._interlink_graphs(mention, sensor, experience, observation, use_sensor)

        if utterance.type == UtteranceType.STATEMENT:
            statement, actor, make_friend = self._create_events(utterance, UtteranceType.STATEMENT, context)
            mention, attribution = self._create_perspective_graph(utterance, statement, UtteranceType.STATEMENT)
            self._interlink_graphs(mention, actor, statement, claim, make_friend)

    def _interlink_graphs(self, mention, actor, subevent, claim, interaction):

        # Link mention and its properties like actor and event
        self.perspective_graph.add((mention.id, self.namespaces['GRASP']['wasAttributedTo'], actor.id))
        self.perspective_graph.add((mention.id, self.namespaces['PROV']['wasDerivedFrom'], subevent.id))

        # Bidirectional link between mention and claim
        self.claim_graph.add((claim.id, self.namespaces['GRASP']['denotedBy'], mention.id))
        self.perspective_graph.add((mention.id, self.namespaces['GRASP']['denotes'], claim.id))

        # Link mention to the interaction
        self.claim_graph.add((interaction.id, self.namespaces['GRASP']['denotedBy'], mention.id))

    def _create_perspective_graph(self, utterance, subevent, claim_type, detection=None):
        if claim_type == UtteranceType.STATEMENT:
            certainty_value = confidence_to_certainty_value(utterance.perspective.certainty)
            polarity_value = polarity_to_polarity_value(utterance.perspective.polarity)
            sentiment_value = sentiment_to_sentiment_value(utterance.perspective.sentiment)
            perspective_values = {'CertaintyValue': certainty_value, 'PolarityValue': polarity_value,
                                  'SentimentValue': sentiment_value}
            mention_unit = 'char'
            mention_position = '0-%s' % len(utterance.transcript)
        else:
            scores = [x.confidence for x in utterance.context.objects] + [x.confidence for x in
                                                                          utterance.context.people]
            certainty_value = confidence_to_certainty_value(sum(scores) / float(len(scores)))
            perspective_values = {'CertaintyValue': certainty_value}
            mention_unit = 'pixel'
            mention_position = '0-%s' % (len(scores))

        # Mention
        mention_label = '%s_%s%s' % (subevent.label, mention_unit, mention_position)
        mention = self._rdf_builder.fill_entity(mention_label, ['Mention'], 'LTa')
        self._link_entity(mention, self.perspective_graph)

        # Attribution
        attribution_label = mention_label + '_%s' % certainty_value
        attribution = self._rdf_builder.fill_entity(attribution_label, ['Attribution'], 'LTa')
        self._link_entity(attribution, self.perspective_graph)

        for typ, val in perspective_values.iteritems():
            attribution_value = self._rdf_builder.fill_entity(val, ['AttributionValue', typ], 'GRASP')
            self._link_entity(attribution_value, self.perspective_graph)
            self.perspective_graph.add((attribution.id, RDF.value, attribution_value.id))

        # Bidirectional link between mention and attribution
        self.perspective_graph.add((mention.id, self.namespaces['GRASP']['hasAttribution'], attribution.id))
        self.perspective_graph.add((attribution.id, self.namespaces['GRASP']['isAttributionFor'], mention.id))

        # Bidirectional link between mention and individual instances
        if claim_type == UtteranceType.STATEMENT:
            self.instance_graph.add((utterance.triple.subject.id, self.namespaces['GRASP']['denotedIn'], mention.id))
            self.instance_graph.add((utterance.triple.complement.id, self.namespaces['GRASP']['denotedIn'], mention.id))
            self.perspective_graph.add(
                (mention.id, self.namespaces['GRASP']['containsDenotation'], utterance.triple.subject.id))
            self.perspective_graph.add(
                (mention.id, self.namespaces['GRASP']['containsDenotation'], utterance.triple.complement.id))
        else:
            self.instance_graph.add((detection.id, self.namespaces['GRASP']['denotedIn'], mention.id))
            self.perspective_graph.add((mention.id, self.namespaces['GRASP']['containsDenotation'], detection.id))

        return mention, attribution

    def _model_graphs_(self, utterance):
        # Leolani world (includes instance and claim graphs)
        claim = self._create_instance_graph(utterance)

        # Leolani talk (includes interaction and perspective graphs)
        self._create_interaction_graph(utterance, claim)

        self._log.info("Triple: {}".format(utterance.triple))

        return claim

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
                           utterance.triple.complement_name,
                           utterance.triple.predicate_name)

        # Query complement
        elif utterance.triple.complement_name == empty:
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
                                ?v rdf:type grasp:CertaintyValue .
                            }
                    """ % (utterance.triple.predicate_name,
                           utterance.triple.subject_name,
                           utterance.triple.complement_name,
                           utterance.triple.predicate_name)

        query = self.query_prefixes + query

        return query

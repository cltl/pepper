from pepper.brain.utils.helper_functions import hash_claim_id, casefold_text, \
    confidence_to_certainty_value, polarity_to_polarity_value, sentiment_to_sentiment_value, get_object_id
from pepper.brain.utils.constants import NAMESPACE_MAPPING

from pepper.language.utils.atoms import UtteranceType

from rdflib import RDF, RDFS, OWL


######################################## Helpers for statement processing ########################################
def _link_leolani(self):
    if self.myself is None:
        # Create Leolani
        self.myself = self._rdf_builder.fill_entity('leolani', ['robot'], 'LW')

    _link_entity(self, self.myself, self.instance_graph)


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


def _link_detections(self, context, dect, prdt):
    # Bidirectional link to context
    self.interaction_graph.add((context.id, self.namespaces['EPS']['hasDetection'], dect.id))
    self.instance_graph.add((dect.id, self.namespaces['EPS']['hasContext'], context.id))
    # Create detection
    detection = create_claim_graph(self, self.myself, prdt, dect, UtteranceType.EXPERIENCE)
    self.claim_graph.add((detection.id, self.namespaces['EPS']['hasContext'], context.id))

    return detection


def _create_detections(self, cntxt, context):
    """

    Parameters
    ----------
    self : brain
    cntxt: Context
    context: Entity
    """
    # Get ids of existing objects in this location
    memory = self.location_reasoner.get_location_memory(cntxt)

    # Detections: objects
    _link_leolani(self)
    prdt = self._rdf_builder.fill_predicate('see')
    object_type = self._rdf_builder.create_resource_uri('N2MU', 'object')
    instances = []
    observations = []

    for item in cntxt.objects:
        if item.name.lower() != 'person':
            # Create instance
            mem_id, memory = get_object_id(memory, item.name)
            objct_id = self._rdf_builder.fill_literal(mem_id, datatype=self.namespaces['XML']['string'])
            objct = self._rdf_builder.fill_entity(casefold_text('%s %s' % (item.name, objct_id), format='triple'),
                                                  [casefold_text(item.name, format='triple'), 'Instance', 'object'],
                                                  'LW')

            # Link detection to graph
            _link_entity(self, objct, self.instance_graph)
            self.interaction_graph.add((objct.id, self.namespaces['N2MU']['id'], objct_id))
            instances.append(objct)

            # Link to context
            detection = _link_detections(self, context, objct, prdt)
            observations.append(detection)

            # Open ended learning
            learnable_type = self._rdf_builder.create_resource_uri('N2MU',
                                                                   casefold_text(item.name, format='triple'))
            self.ontology_graph.add((learnable_type, RDFS.subClassOf, object_type))

    # Detections: faces
    for item in cntxt.people:
        if item.name.lower() != item.UNKNOWN.lower():
            # Create instance
            prsn = self._rdf_builder.fill_entity(casefold_text(item.name, format='triple'), ['person', 'Instance'],
                                                 'LW')

            # Link detection to graph
            _link_entity(self, prsn, self.instance_graph)
            instances.append(prsn)

            # Link to context
            detection = _link_detections(self, context, prsn, prdt)
            observations.append(detection)

    return instances, observations


def _create_context(self, cntxt):
    # Create an episodic awareness by making a context
    context_id = self._rdf_builder.fill_literal(cntxt.id, datatype=self.namespaces['XML']['string'])
    context = self._rdf_builder.fill_entity('context%s' % cntxt.id, ['Context'], 'LC')
    _link_entity(self, context, self.interaction_graph)
    self.interaction_graph.add((context.id, self.namespaces['N2MU']['id'], context_id))

    # Time
    time = self._rdf_builder.fill_entity(cntxt.datetime.strftime('%Y-%m-%d'), ['Time', 'DateTimeDescription'], 'LC')
    _link_entity(self, time, self.interaction_graph)
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
        # City level
        location_city = self._rdf_builder.fill_entity(cntxt.location.city, ['location', 'city', 'Place'], 'LW')
        _link_entity(self, location_city, self.interaction_graph)
        # Country level
        location_country = self._rdf_builder.fill_entity(cntxt.location.country, ['location', 'country', 'Place'],
                                                         'LW')
        _link_entity(self, location_country, self.interaction_graph)
        # Region level
        location_region = self._rdf_builder.fill_entity(cntxt.location.region, ['location', 'region', 'Place'],
                                                        'LW')
        _link_entity(self, location_region, self.interaction_graph)

        # Create location
        location_label = casefold_text('%s' % cntxt.location.label, format='triple')
        location_id = self._rdf_builder.fill_literal(cntxt.location.id, datatype=self.namespaces['XML']['string'])

        if cntxt.location.label.lower() == cntxt.location.UNKNOWN.lower():
            # All unknowns have label Unknown, different ids but iri with id
            uri_suffix = casefold_text('%s%s' % (cntxt.location.label, cntxt.location.id), format='triple')
            location_uri = self._rdf_builder.create_resource_uri('LC', uri_suffix)
            location = self._rdf_builder.fill_entity(location_label, ['location', 'Place'], 'LC', uri=location_uri)

        else:
            # If hospital exists and has an id then use that id, if it does not exist then add id
            ids = self.get_id_of_instance(location_label)
            if ids:
                location_id = self._rdf_builder.fill_literal(ids[0], datatype=self.namespaces['XML']['string'])

            location = self._rdf_builder.fill_entity(location_label, ['location', 'Place'], 'LC')

        _link_entity(self, location, self.interaction_graph)
        self.interaction_graph.add((location.id, self.namespaces['N2MU']['id'], location_id))
        self.interaction_graph.add((location.id, self.namespaces['N2MU']['in'], location_city.id))
        self.interaction_graph.add((location.id, self.namespaces['N2MU']['in'], location_country.id))
        self.interaction_graph.add((location.id, self.namespaces['N2MU']['in'], location_region.id))
        self.interaction_graph.add((context.id, self.namespaces['SEM']['hasPlace'], location.id))

    # Detections
    instances, observations = _create_detections(self, cntxt, context)

    return context, instances, observations


def _create_actor(self, utterance, claim_type):
    if claim_type == UtteranceType.STATEMENT:
        source = utterance.chat_speaker
        source_type = 'person'
        ns = 'LF'
        pred = 'know'

    else:
        source = 'front-camera'
        source_type = 'sensor'
        ns = 'LI'
        pred = 'sense'

    # Actor
    actor = self._rdf_builder.fill_entity(source, ['Instance', 'Source', 'Actor', source_type], ns)
    _link_entity(self, actor, self.interaction_graph)

    # Add leolani knows/senses actor
    predicate = self._rdf_builder.fill_predicate(pred)
    interaction = create_claim_graph(self, self.myself, predicate, actor, claim_type)

    # Add actor (friend) is same as person(world)
    if 'person' in actor.types:
        person = self._rdf_builder.fill_entity('%s' % actor.label, ['Instance', 'person'], 'LW')
        _link_entity(self, person, self.instance_graph)
        self.claim_graph.add((actor.id, OWL.sameAs, person.id))

    return actor, interaction


def _create_events(self, utterance, claim_type, context):
    # Chat or Visual
    event_id = self._rdf_builder.fill_literal(utterance.chat.id, datatype=self.namespaces['XML']['string'])
    event_type = '%s' % ('chat' if claim_type == UtteranceType.STATEMENT else 'visual')
    eventt_label = '%s%s' % (event_type, str(event_id))
    event = self._rdf_builder.fill_entity(eventt_label, ['Event', '%s' % event_type.title()], 'LTa')
    _link_entity(self, event, self.interaction_graph)
    self.interaction_graph.add((event.id, self.namespaces['N2MU']['id'], event_id))
    self.interaction_graph.add((context.id, self.namespaces['SEM']['hasEvent'], event.id))

    # Utterance or Detection are events and instances  # TODO incremental detection instead of id of utterance
    subevent_id = self._rdf_builder.fill_literal(utterance.turn, datatype=self.namespaces['XML']['string'])
    subevent_type = '%s' % ('utterance' if claim_type == UtteranceType.STATEMENT else 'detection')
    subevent_label = '%s_%s%s' % (str(event.label), subevent_type, str(subevent_id))
    subevent = self._rdf_builder.fill_entity(subevent_label, ['Event', '%s' % subevent_type.title()], 'LTa')
    _link_entity(self, subevent, self.interaction_graph)

    # Actor
    actor, interaction = _create_actor(self, utterance, claim_type)
    self.interaction_graph.add((subevent.id, self.namespaces['N2MU']['id'], subevent_id))
    self.interaction_graph.add((subevent.id, self.namespaces['SEM']['hasActor'], actor.id))
    self.interaction_graph.add((event.id, self.namespaces['SEM']['hasSubEvent'], subevent.id))

    return subevent, actor, interaction


def _create_mention(self, utterance, subevent, claim_type, detection):
    if claim_type == UtteranceType.STATEMENT:
        mention_unit = 'char'
        mention_position = '0-%s' % len(utterance.transcript)
        transcript = self._rdf_builder.fill_literal(utterance.transcript, datatype=self.namespaces['XML']['string'])
    else:
        scores = [x.confidence for x in utterance.context.objects] + [x.confidence for x in
                                                                      utterance.context.people]
        mention_unit = 'pixel'
        mention_position = '0-%s' % len(scores)

    # Mention
    mention_label = '%s_%s%s' % (subevent.label, mention_unit, mention_position)
    mention = self._rdf_builder.fill_entity(mention_label, ['Mention', claim_type.name.title()], 'LTa')
    _link_entity(self, mention, self.perspective_graph)

    # Bidirectional link between mention and individual instances
    if claim_type == UtteranceType.STATEMENT:
        self.instance_graph.add((utterance.triple.subject.id, self.namespaces['GAF']['denotedIn'], mention.id))
        self.instance_graph.add((utterance.triple.complement.id, self.namespaces['GAF']['denotedIn'], mention.id))
        self.perspective_graph.add(
            (mention.id, self.namespaces['GAF']['containsDenotation'], utterance.triple.subject.id))
        self.perspective_graph.add(
            (mention.id, self.namespaces['GAF']['containsDenotation'], utterance.triple.complement.id))
        self.perspective_graph.add((mention.id, RDF.value, transcript))
    else:
        self.instance_graph.add((detection.id, self.namespaces['GAF']['denotedIn'], mention.id))
        self.perspective_graph.add((mention.id, self.namespaces['GAF']['containsDenotation'], detection.id))

    return mention


def _create_attribution(self, utterance, mention, claim, claim_type=None, perspective_values=None):
    if perspective_values:
        attribution_suffix = '-'.join([perspective_values[k] for k in sorted(perspective_values)])

    elif claim_type == UtteranceType.STATEMENT:
        certainty_value = confidence_to_certainty_value(utterance.perspective.certainty)
        polarity_value = polarity_to_polarity_value(utterance.perspective.polarity)
        sentiment_value = sentiment_to_sentiment_value(utterance.perspective.sentiment)
        perspective_values = {'CertaintyValue': certainty_value, 'PolarityValue': polarity_value,
                              'SentimentValue': sentiment_value}
        attribution_suffix = '%s-%s-%s' % (certainty_value, polarity_value, sentiment_value)
    else:
        scores = [x.confidence for x in utterance.context.objects] + [x.confidence for x in
                                                                      utterance.context.people]
        certainty_value = confidence_to_certainty_value(sum(scores) / float(len(scores)))
        perspective_values = {'CertaintyValue': certainty_value}
        attribution_suffix = '%s' % certainty_value

    attribution_label = claim.label + '_%s' % attribution_suffix
    attribution = self._rdf_builder.fill_entity(attribution_label, ['Attribution'], 'LTa')
    _link_entity(self, attribution, self.perspective_graph)

    for typ, val in perspective_values.iteritems():
        if typ in ['FactualityValue', 'CertaintyValue', 'TemporalValue', 'PolarityValue']:
            ns = 'GRASPf'
        elif typ in ['SentimentValue']:
            ns = 'GRASPs'
        elif typ in ['EmotionValue']:
            ns = 'GRASPe'
        else:
            ns = 'GRASP'

        attribution_value = self._rdf_builder.fill_entity(val, ['AttributionValue', typ], ns)
        _link_entity(self, attribution_value, self.perspective_graph)
        self.perspective_graph.add((attribution.id, RDF.value, attribution_value.id))

    # Bidirectional link between mention and attribution
    self.perspective_graph.add((mention.id, self.namespaces['GRASP']['hasAttribution'], attribution.id))
    self.perspective_graph.add((attribution.id, self.namespaces['GRASP']['isAttributionFor'], mention.id))

    return attribution


def create_instance_graph(self, utterance):
    # type (Utterance) -> Graph, Graph, str, str, str
    """
    Create linked data related to what leolani learned/knows about the world
    Parameters
    ----------
    self:
    utterance: Utterance

    Returns
    -------
    claim: claim graph


    """
    _link_leolani(self)
    # Subject
    if utterance.type == UtteranceType.STATEMENT:
        utterance.triple.subject.add_types(['Instance'])
        _link_entity(self, utterance.triple.subject, self.instance_graph)
    elif utterance.type == UtteranceType.EXPERIENCE:
        _link_leolani(self)

    # Complement
    utterance.triple.complement.add_types(['Instance'])
    _link_entity(self, utterance.triple.complement, self.instance_graph)

    # Claim graph
    predicate = utterance.triple.predicate if utterance.type == UtteranceType.STATEMENT \
        else self._rdf_builder.fill_predicate('see')

    claim = create_claim_graph(self, utterance.triple.subject, predicate, utterance.triple.complement,
                               utterance.type)

    return claim


def create_claim_graph(self, subject, predicate, complement, claim_type=UtteranceType.STATEMENT):
    # Statement
    claim_label = hash_claim_id([subject.label, predicate.label, complement.label])

    claim = self._rdf_builder.fill_entity(claim_label, ['Event', 'Assertion'], 'LW')
    _link_entity(self, claim, self.claim_graph)

    # Create graph and add triple
    graph = self.dataset.graph(claim.id)
    graph.add((subject.id, predicate.id, complement.id))

    return claim


def create_interaction_graph(self, utterance, claim):
    # Add context
    context, detections, observations = _create_context(self, utterance.context)

    # Subevents
    experience, sensor, use_sensor = _create_events(self, utterance, UtteranceType.EXPERIENCE, context)
    for detection, observation in zip(detections, observations):
        mention, attribution = create_perspective_graph(self, utterance, claim, experience, UtteranceType.EXPERIENCE,
                                                        detection=detection)
        interlink_graphs(self, mention, sensor, experience, observation, use_sensor)

    if utterance.type == UtteranceType.STATEMENT:
        statement, actor, make_friend = _create_events(self, utterance, UtteranceType.STATEMENT, context)
        mention, attribution = create_perspective_graph(self, utterance, claim, statement, UtteranceType.STATEMENT)
        interlink_graphs(self, mention, actor, statement, claim, make_friend)


def create_perspective_graph(self, utterance, claim, subevent, claim_type, detection=None):
    # Mention
    mention = _create_mention(self, utterance, subevent, claim_type, detection=detection)

    # Attribution
    attribution = _create_attribution(self, utterance, mention, claim, claim_type=claim_type)

    return mention, attribution


def interlink_graphs(self, mention, actor, subevent, claim, interaction):
    # Link mention and its properties like actor and event
    self.perspective_graph.add((mention.id, self.namespaces['GRASP']['wasAttributedTo'], actor.id))
    self.perspective_graph.add((mention.id, self.namespaces['PROV']['wasDerivedFrom'], subevent.id))

    # Bidirectional link between mention and claim
    self.claim_graph.add((claim.id, self.namespaces['GAF']['denotedBy'], mention.id))
    self.perspective_graph.add((mention.id, self.namespaces['GAF']['denotes'], claim.id))

    # Link mention to the interaction TODO: revise with Piek
    # self.claim_graph.add((interaction.id, self.namespaces['GAF']['denotedBy'], mention.id))


def model_graphs(self, utterance):
    # Leolani world (includes instance and claim graphs)
    claim = create_instance_graph(self, utterance)

    # Leolani talk (includes interaction and perspective graphs)
    create_interaction_graph(self, utterance, claim)

    self._log.info("Triple: {}".format(utterance.triple))

    return claim

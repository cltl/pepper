from pepper.brain.infrastructure import CardinalityConflict, NegationConflict, StatementNovelty, EntityNovelty, \
    Gap, Gaps, Overlap, Overlaps
from pepper.brain.utils.helper_functions import read_query
from pepper.brain.basic_brain import BasicBrain

from pepper import config


class ThoughtGenerator(BasicBrain):

    def __init__(self, address=config.BRAIN_URL_LOCAL, clear_all=False):
        # type: (str, bool) -> ThoughtGenerator
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        super(ThoughtGenerator, self).__init__(address, clear_all, is_submodule=True)

    ########## novelty ##########
    def _fill_statement_novelty_(self, raw_provenance):
        """
        Structure statement novelty to get provenance if this statement has been heard before
        Parameters
        ----------
        raw_provenance: dict
            standard row result from SPARQL

        Returns
        -------
            StatementNovelty object containing provenance
        """
        preprocessed_date = self._rdf_builder.label_from_uri(raw_provenance['date']['value'], 'LC')
        processed_provenance = self._rdf_builder.fill_provenance(raw_provenance['authorlabel']['value'],
                                                                 preprocessed_date)

        return StatementNovelty(processed_provenance)

    def fill_entity_novelty(self, subject_url, complement_url):
        """
        Structure entity novelty to signal if these entities have been heard before
        Parameters
        ----------
        subject_url: str
            URI of instance
        complement_url: str
            URI of instance

        Returns
        -------
            Entity object containing boolean values signaling if they are new
        """
        subject_novelty = self._check_instance_novelty_(subject_url)
        complement_novelty = self._check_instance_novelty_(complement_url)

        return EntityNovelty(subject_novelty, complement_novelty)

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

    def _check_instance_novelty_(self, instance_url):
        """
        Query if an instance (entity) has been heard about before
        Parameters
        ----------
        instance_url: str
            URI of instance

        Returns
        -------
        response: List[StatementNovelty]
            List of provenance for the instance
        """
        query = read_query('thoughts/entity_novelty') % instance_url
        response = self._submit_query(query, ask=True)

        return response

    ########## gaps ##########
    def _fill_entity_gap_(self, raw_response):
        """
        Structure entity gap to get the predicate and range of what has been learned but not heard
        Parameters
        ----------
        raw_response: dict
            standard row result from SPARQL

        Returns
        -------
            Gap object containing a predicate and its range
        """

        processed_predicate = self._rdf_builder.fill_predicate(raw_response['p']['value'].split('/')[-1])
        processed_range = self._rdf_builder.fill_entity('', namespace='N2MU',
                                                        types=[raw_response['type2']['value'].split('/')[-1]])

        return Gap(processed_predicate, processed_range)

    def get_entity_gaps(self, entity, exclude=None):
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
        query = read_query('thoughts/subject_gaps') % (entity.label, entity.label if exclude is None else exclude.label)
        response = self._submit_query(query)

        if response:
            subject_gaps = [self._fill_entity_gap_(elem)
                            for elem in response
                            if elem['p']['value'].split('/')[-1] not in self._NOT_TO_ASK_PREDICATES]

        else:
            subject_gaps = []

        # Role as object
        query = read_query('thoughts/object_gaps') % (entity.label, entity.label if exclude is None else exclude.label)
        response = self._submit_query(query)

        if response:
            complement_gaps = [self._fill_entity_gap_(elem)
                               for elem in response
                               if elem['p']['value'].split('/')[-1] not in self._NOT_TO_ASK_PREDICATES]

        else:
            complement_gaps = []

        return Gaps(subject_gaps, complement_gaps)

    ########## overlaps ##########
    def _fill_overlap_(self, raw_response):
        """
        Structure overlap to get the provenance and entity on which they overlap
        Parameters
        ----------
        raw_response: dict
            standard row result from SPARQL

        Returns
        -------
            Overlap object containing an entity and the provenance of the mention causing the overlap
        """
        preprocessed_date = self._rdf_builder.label_from_uri(raw_response['date']['value'], 'LC')
        preprocessed_types = self._rdf_builder.clean_aggregated_types(raw_response['types']['value'])

        processed_provenance = self._rdf_builder.fill_provenance(raw_response['authorlabel']['value'],
                                                                 preprocessed_date)
        processed_entity = self._rdf_builder.fill_entity(raw_response['label']['value'], preprocessed_types, 'LW')

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
        query = read_query('thoughts/object_overlap') % (
        utterance.triple.predicate_name, utterance.triple.complement_name,
        utterance.triple.subject_name)
        response = self._submit_query(query)

        if response[0]['types']['value'] != '':
            complement_overlap = [self._fill_overlap_(elem) for elem in response]
        else:
            complement_overlap = []

        # Role as object
        query = read_query('thoughts/subject_overlap') % (
            utterance.triple.predicate_name, utterance.triple.subject_name,
            utterance.triple.complement_name)
        response = self._submit_query(query)

        if response[0]['types']['value'] != '':
            subject_overlap = [self._fill_overlap_(elem) for elem in response]
        else:
            subject_overlap = []

        return Overlaps(subject_overlap, complement_overlap)

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
        processed_polarity = self._rdf_builder.label_from_uri(raw_conflict['val']['value'], 'GRASPf')

        return NegationConflict(processed_provenance, processed_polarity)

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

    def get_complement_cardinality_conflicts(self, utterance):
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
        if str(utterance.triple.predicate_name) not in self._ONE_TO_ONE_PREDICATES:
            return []

        query = read_query('thoughts/object_cardinality_conflicts') % (utterance.triple.predicate_name,
                                                                       utterance.triple.subject_name,
                                                                       utterance.triple.complement_name)

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
        query = read_query('thoughts/negation_conflicts') % (utterance.triple.predicate_name,
                                                             utterance.triple.subject_name,
                                                             utterance.triple.complement_name)

        response = self._submit_query(query)
        if response[0] != {}:
            conflicts = [self._fill_negation_conflict_(elem) for elem in response]
        else:
            conflicts = []

        return conflicts

    def get_trust(self, speaker):
        """
        Compute a value of trust based on what is know about and via this person
        Parameters
        ----------
        speaker

        Returns
        -------
        trust_value: float
            Weighted average of features
        """

        # chat based feature
        num_chats = float(self.count_chat_with(speaker))
        friends = self.get_best_friends()
        best_friend_chats = float(friends[0][1])
        chat_feature = num_chats / best_friend_chats

        # new content feature
        num_claims = float(self.count_statements_by(speaker))
        all_claims = float(self.count_statements())
        claims_feature = num_claims / all_claims

        # conflicts feature
        num_conflicts = float(len(self.get_conflicts_by(speaker)))
        all_conflicts = float(len(self.get_conflicts()))
        conflicts_feature = (num_conflicts / all_conflicts) - 1

        # Aggregate
        # TODO scale
        trust_value = (chat_feature + claims_feature + conflicts_feature) / 3

        return trust_value

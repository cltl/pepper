from pepper.brain.utils.helper_functions import read_query, casefold_text
from pepper.brain.reasoners import LocationReasoner, ThoughtGenerator, TypeReasoner
from pepper.brain.infrastructure import Thoughts
from pepper.brain.basic_brain import BasicBrain

from pepper.brain.LTM_question_processing import create_query
from pepper.brain.LTM_statement_processing import model_graphs

from pepper import config


class LongTermMemory(BasicBrain):
    def __init__(self, address=config.BRAIN_URL_LOCAL, clear_all=False):
        # type: (str, bool) -> None
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

            # TODO: Ongoing work
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
        reason_types: Boolean
            Signal to entity linking over the semantic web

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
            instance = model_graphs(self, utterance)

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
            cardinality_conflict = self.thought_generator.get_complement_cardinality_conflicts(utterance)

            # Check for gaps, in case we want to be proactive
            subject_gaps = self.thought_generator.get_entity_gaps(utterance.triple.subject,
                                                                  exclude=utterance.triple.complement)
            complement_gaps = self.thought_generator.get_entity_gaps(utterance.triple.complement,
                                                                     exclude=utterance.triple.subject)

            # Report trust
            trust = self.thought_generator.get_trust(utterance.chat_speaker)

            # Create JSON output
            thoughts = Thoughts(statement_novelty, entity_novelty, negation_conflicts, cardinality_conflict,
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
        _ = model_graphs(self, utterance)
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
        query = create_query(self, utterance)
        self._log.info("Triple: {}".format(utterance.triple))

        # Perform query
        response = self._submit_query(query)

        # Create JSON output
        output = {'response': response, 'question': utterance}

        return output

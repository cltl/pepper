from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import visuals

from pepper.language.generation.thoughts_phrasing import phrase_thoughts, _phrase_cardinality_conflicts, \
    _phrase_negation_conflicts, _phrase_statement_novelty, _phrase_type_novelty, _phrase_subject_gaps, \
    _phrase_object_gaps, _phrase_overlaps, phrase_trust

from test.brain.sandbox import transform_capsule

from random import choice

# Create brain connection
brain = LongTermMemory()
bl = [True, False]

flat_list = [item for detection in visuals for item in detection]
experience =set(flat_list)

for elem in experience:
    x = brain.get_thoughts_on_entity(elem, reason_types=True)

    print('\t\t\tFINAL SAY: ' + phrase_thoughts(x, proactive=True, persist=True))

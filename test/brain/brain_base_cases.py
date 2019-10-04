from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements

from pepper.language.generation.thoughts_phrasing import phrase_thoughts, _phrase_cardinality_conflicts, \
    _phrase_negation_conflicts, _phrase_statement_novelty, _phrase_type_novelty, _phrase_subject_gaps, \
    _phrase_object_gaps, _phrase_overlaps, phrase_trust

from test.brain.utils import transform_capsule, bl

from random import choice

if __name__ == "__main__":

    # Create brain connection
    brain = LongTermMemory()

    for elem in statements:
        em = choice(bl)
        np = choice(bl)
        p = choice(bl)
        capsule = transform_capsule(elem, empty=em, no_people=np, place=p)
        x = brain.update(capsule)

        print(elem['subject']['label'], elem['predicate']['type'], elem['object']['label'])
        print('\tcardinality conflicts: ' + _phrase_cardinality_conflicts(x['cardinality_conflicts'], elem))
        print('\tnegation conflicts: ' + _phrase_negation_conflicts(x['negation_conflicts'], elem))
        print('\tstatement novelty: ' + _phrase_statement_novelty(x['statement_novelty']))
        print('\ttype novelty: ' + _phrase_type_novelty(x['entity_novelty'], elem))
        print('\tsubject gaps: ' + _phrase_subject_gaps(x['subject_gaps'], elem))
        print('\tobject gaps: ' + _phrase_object_gaps(x['object_gaps'], elem))
        print('\toverlaps: ' + _phrase_overlaps(x['overlaps'], elem))
        print('\ttrust: ' + phrase_trust(x['trust']))

        print('\t\t\tFINAL SAY: ' + phrase_thoughts(x, proactive=True, persist=True))

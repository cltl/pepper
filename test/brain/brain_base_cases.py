from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import statements

from pepper.language.generation.thoughts_phrasing import phrase_thoughts, _phrase_cardinality_conflicts, \
    _phrase_negation_conflicts, _phrase_statement_novelty, _phrase_type_novelty, _phrase_subject_gaps, \
    _phrase_complement_gaps, _phrase_overlaps, phrase_trust

from test.brain.utils import transform_capsule, binary_values

from random import choice

if __name__ == "__main__":

    # Create brain connection
    brain = LongTermMemory(clear_all=True)

    for elem in statements:
        em = choice(binary_values)
        np = choice(binary_values)
        p = choice(binary_values)
        capsule = transform_capsule(elem, empty=em, no_people=np, place=p)
        x = brain.update(capsule)
        thoughts = x['thoughts']
        utterance = x['statement']

        try:
            print('\tcardinality conflicts: ' + _phrase_cardinality_conflicts(thoughts.complement_conflicts(),
                                                                              utterance))
        except:
            print('\tcardinality conflicts: ' + 'No say')
        try:
            print('\tnegation conflicts: ' + _phrase_negation_conflicts(thoughts.negation_conflicts(), utterance))
        except:
            print('\tnegation conflicts: ' + 'No say')
        try:
            print('\tstatement novelty: ' + _phrase_statement_novelty(thoughts.statement_novelties(), utterance))
        except:
            print('\tstatement novelty: ' 'No say')
        try:
            print('\ttype novelty: ' + _phrase_type_novelty(thoughts.entity_novelty(), utterance))
        except:
            print('\ttype novelty: ' + 'No say')
        try:
            print('\tsubject gaps: ' + _phrase_subject_gaps(thoughts.subject_gaps(), utterance))
        except:
            print('\tsubject gaps: ' + 'No say')
        try:
            print('\tobject gaps: ' + _phrase_complement_gaps(thoughts.complement_gaps(), utterance))
        except:
            print('\tobject gaps: ' + 'No say')
        try:
            print('\toverlaps: ' + _phrase_overlaps(thoughts.overlaps(), utterance))
        except:
            print('\toverlaps: ' + 'No say')
        try:
            print('\t\t\tFINAL SAY: ' + phrase_thoughts(x, proactive=True, persist=True))
        except:
            print('\t\t\tFINAL SAY: ' + 'No say')

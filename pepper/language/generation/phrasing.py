import random
from datetime import datetime

from pepper.brain.utils.helper_functions import casefold, casefold_capsule
from pepper.knowledge.sentences import NEW_KNOWLEDGE, EXISTING_KNOWLEDGE, CONFLICTING_KNOWLEDGE, CURIOSITY, HAPPY, \
    TRUST, NO_TRUST


def replace_pronouns(author, speaker, subject):
    pronoun = None

    if subject in ['Leolani', 'leolani']:
        pronoun = 'I'

    return pronoun


def phrase_all_conflicts(conflicts, speaker=None):
    say = 'I have %s conflicts in my brain.' % len(conflicts)
    conflict = random.choice(conflicts)

    # Conflict of subject
    if len(conflict['objects']) > 1:
        predicate = casefold(conflict['predicate'], format='natural')
        options = ['%s %s like %s told me' % (predicate, item['value'], item['author']) for item in conflict['objects']]
        options = ' or '.join(options)
        subject = replace_pronouns(conflict['objects'][1]['author'], speaker, conflict['subject'])

        say = say + ' For example, I do not know if %s %s' % (subject, options)

    return say


def phrase_cardinality_conflicts(conflicts, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    # There is no conflict, so just be happy to learn
    if not conflicts[0]:
        say = random.choice(NEW_KNOWLEDGE)

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)
        conflict = random.choice(conflicts)
        x = 'you' if conflict.author == capsule['author'] else conflict.author
        y = 'you' if capsule['subject']['label'] == conflict.author else capsule['subject']['label']

        say += ' %s told me in %s that %s %s %s, but now you tell me that %s %s %s' \
               % (x,
                  conflict.date.strftime("%B"),
                  casefold(y, format='natural'), capsule['predicate']['type'],
                  casefold(conflict.object_name, format='natural'),
                  casefold(y, format='natural'), capsule['predicate']['type'], capsule['object']['label'])

    return say


def phrase_negation_conflicts(conflicts, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    # There is no conflict entries, so just be happy to learn
    if not conflicts[0]:
        say = random.choice(NEW_KNOWLEDGE)

    # There is conflict entries
    else:

        affirmative_conflict = [item for item in conflicts if not item.predicate_name.endswith('-not')]
        negative_conflict = [item for item in conflicts if item.predicate_name.endswith('-not')]

        # There is a conflict, so we phrase it
        if affirmative_conflict and negative_conflict:
            say = random.choice(CONFLICTING_KNOWLEDGE)

            affirmative_conflict = random.choice(affirmative_conflict)
            negative_conflict = random.choice(negative_conflict)

            say += ' %s told me in %s that %s %s %s, but in %s %s told me that %s did not %s %s' \
                   % (casefold(affirmative_conflict.author, format='natural'), affirmative_conflict.date.strftime("%B"),
                      capsule['subject']['label'], affirmative_conflict.predicate_name, capsule['object']['label'],
                      negative_conflict.date.strftime("%B"), casefold(negative_conflict.author, format='natural'),
                      capsule['subject']['label'], affirmative_conflict.predicate_name, capsule['object']['label'])

        # There is no conflict, so just be happy to learn
        else:
            say = random.choice(NEW_KNOWLEDGE)

    return say


def phrase_statement_novelty(novelties):
    # I do not know this before, so be happy to learn
    if not novelties[0]:
        say = random.choice(NEW_KNOWLEDGE)

    # I already knew this
    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        novelty = random.choice(novelties)

        say += ' %s told me about it in %s' % (casefold(novelty.author, format='natural'), novelty.date.strftime("%B"))

    return say


def phrase_type_novelty(novelties, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    entity_role = random.choice(['subject', 'object'])
    novelty = novelties.subject if entity_role == 'subject' else novelties.object

    if novelty:
        say = random.choice(NEW_KNOWLEDGE)
        say += ' I have never heard about %s before!' % capsule[entity_role]['label']

    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        say += ' I know about %s.' % capsule[entity_role]['label']

    return say


def phrase_subject_gaps(all_gaps, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    entity_role = random.choice(['subject', 'object'])
    gaps = all_gaps.subject if entity_role == 'subject' else all_gaps.object

    if entity_role == 'subject':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s %s' % (capsule['subject']['label'],
                                              casefold(capsule['predicate']['type'], format='natural'))

        else:
            gap = random.choice(gaps)
            range = casefold(' or '.join(gap.entity_range), format='natural')
            say += ' Has a %s ever been %s %s?' % (range, casefold(gap.predicate_name, format='natural'),
                                                       capsule['subject']['label'])

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s a %s like %s' % (casefold(capsule['predicate']['type'], format='natural'),
                                                        capsule['object']['type'], capsule['object']['label'])

        else:
            gap = random.choice(gaps)
            range = casefold(' or '.join(gap.entity_range), format='natural')
            if '#' in range:
                say += ' What is %s %s?' % (capsule['subject']['label'], casefold(gap.predicate_name, format='natural'))
            else:
                say += ' Has %s ever %s a %s?' % (capsule['subject']['label'],
                                                  casefold(gap.predicate_name, format='natural'), range)

    return say


def phrase_object_gaps(all_gaps, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    entity_role = random.choice(['subject', 'object'])
    gaps = all_gaps.subject if entity_role == 'subject' else all_gaps.object

    if entity_role == 'subject':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s %s' % (capsule['subject']['label'],
                                              casefold(capsule['predicate']['type'], format='natural'))

        else:
            gap = random.choice(gaps)
            range = casefold(' or '.join(gap.entity_range), format='natural')
            say += ' Has any %s %s %s?' % (range, casefold(gap.predicate_name, format='natural'),
                                               capsule['object']['label'])

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types of %s like %s can be %s' % (capsule['object']['type'], capsule['object']['label'],
                                                            casefold(capsule['predicate']['type'], format='natural'))

        else:
            gap = random.choice(gaps)
            range = casefold(' or '.join(gap.entity_range), format='natural')
            if '#' in range:
                say += ' What is %s %s?' % (capsule['object']['label'], casefold(gap.predicate_name, format='natural'))
            else:
                say += ' What other %s was %s %s?' % (range, capsule['object']['label'],
                                                      casefold(gap.predicate_name, format='natural'))

    return say


def phrase_overlaps(all_overlaps, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    if capsule['object']['type'] == '':
        capsule['object']['type'] = 'thing'

    if capsule['subject']['type'] == '':
        capsule['subject']['type'] = 'thing'

    entity_role = random.choice(['subject', 'object'])
    overlaps = all_overlaps.subject if entity_role == 'subject' else all_overlaps.object

    if not overlaps and entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' I did not know anything that %s %s' % (capsule['subject']['label'], capsule['predicate']['type'])

    elif not overlaps and entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' I did not know anybody who %s %s' % (capsule['predicate']['type'], capsule['object']['label'])

    elif len(overlaps) < 2 and entity_role == 'subject':
        say = random.choice(HAPPY)

        say += ' Did you know that %s also %s %s' % (capsule['subject']['label'], capsule['predicate']['type'],
                                                     random.choice(overlaps).entity_name,)

    elif len(overlaps) < 2 and entity_role == 'object':
        say = random.choice(HAPPY)

        say += ' Did you know that %s also %s %s' % (random.choice(overlaps).entity_name,
                                                     capsule['predicate']['type'], capsule['object']['label'])

    elif entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' Now I know %s items that %s %s, like %s and %s' % (len(overlaps), capsule['subject']['label'],
                                                                    capsule['predicate']['type'],
                                                                    random.choice(overlaps).entity_name,
                                                                    random.choice(overlaps).entity_name)

    elif entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' Now I know %s %s that %s %s, like %s and %s' % (len(overlaps), capsule['subject']['type'],
                                                                 capsule['predicate']['type'],
                                                                 capsule['object']['label'],
                                                                 random.choice(overlaps).entity_name,
                                                                 random.choice(overlaps).entity_name)

    return say


def phrase_trust(trust):
    if trust == 1:
        say = random.choice(TRUST)
    else:
        say = random.choice(NO_TRUST)

    return say


def phrase_update(update, proactive=True, persist=False):
    options = ['cardinality_conflicts', 'negation_conflicts', 'statement_novelty', 'entity_novelty']

    if proactive:
        options.extend(['subject_gaps', 'object_gaps', 'overlaps'])

    approach = random.choice(options)
    thoughts = update['thoughts']

    if approach == 'cardinality_conflicts':
        say = phrase_cardinality_conflicts(thoughts.object_conflict(), update['statement'])

    elif approach == 'negation_conflicts':
        say = phrase_negation_conflicts(thoughts.negation_conflicts(), update['statement'])

    elif approach == 'statement_novelty':
        say = phrase_statement_novelty(thoughts.statement_novelties())

    elif approach == 'entity_novelty':
        say = phrase_type_novelty(thoughts.entity_novelty(), update['statement'])

    elif approach == 'subject_gaps':
        say = phrase_subject_gaps(thoughts.subject_gaps(), update['statement'])

    elif approach == 'object_gaps':
        say = phrase_object_gaps(thoughts.object_gaps(), update['statement'])

    elif approach == 'overlaps':
        say = phrase_overlaps(thoughts.overlaps(), update['statement'])

    if persist and say == '':
        say = phrase_update(update, proactive, persist)

    return say

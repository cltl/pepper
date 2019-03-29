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

        say = say + ' For example, I do not know if %s %s'% (subject, options)

    return say


def phrase_cardinality_conflicts(conflicts, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    # There is no conflict, so just be happy to learn
    if not conflicts:
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
                  casefold(y, format='natural'), capsule['predicate']['type'], casefold(conflict.object.label, format='natural'),
                  casefold(y, format='natural'), capsule['predicate']['type'], capsule['object']['label'])

    return say


def phrase_negation_conflicts(conflict, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    # There is no conflict, so nothing to say
    if conflict == {}:
        say = ''

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)

        say += ' %s told me in %s that %s %s %s, but in %s %s told me that %s did not %s %s' \
            %(conflict['positive']['authorlabel'].replace('_', ' '),
              datetime.strptime(conflict['positive']['date'], "%Y-%m-%d").strftime("%B"),
              capsule['subject']['label'], capsule['predicate']['type'], capsule['object']['label'],
              datetime.strptime(conflict['negative']['date'], "%Y-%m-%d").strftime("%B"),
              conflict['negative']['authorlabel'],
              capsule['subject']['label'], capsule['predicate']['type'], capsule['object']['label'])

    return say


def phrase_statement_novelty(novelty):
    # I do not know this before
    if novelty[0] == {}:
        say = random.choice(NEW_KNOWLEDGE)

    # I already knew this
    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        provenance = random.choice(novelty)

        say += ' %s told me about it in %s' %(provenance['authorlabel'].replace('_', ' '),
                                                datetime.strptime(provenance['date'], "%Y-%m-%d").strftime("%B"))

    return say


def phrase_type_novelty(novelty, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    entity_role = random.choice(novelty.keys())

    if novelty[entity_role]:
        say = random.choice(NEW_KNOWLEDGE)
        say += ' I have never heard about %s before!' % capsule[entity_role]['label']

    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        say += ' I know about %s.' % capsule[entity_role]['label']

    return say


def phrase_subject_gaps(gaps, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    entity_role = random.choice(gaps.keys())

    if not gaps[entity_role]:
        say = ''

    elif entity_role == 'subject':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        if '#' in gap['range']:
            say += ' What is %s %s' % (capsule['subject']['label'], gap['predicate'].replace('_', ' '))

        else:
            say += ' Has %s %s a %s?' %(capsule['subject']['label'],
                                       gap['predicate'].replace('_', ' '), gap['range'].replace('_', ' '))

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        say += ' Is there a %s %s %s?' % (gap['domain'].replace('_', ' '), gap['predicate'].replace('_', ' '),
                                        capsule['subject']['label'])

    return say


def phrase_object_gaps(gaps, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    entity_role = random.choice(gaps.keys())

    if not gaps[entity_role]:
        say = ''

    elif entity_role == 'subject':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        if '#' in gap['range']:
            say += ' What is %s %s' % (capsule['object']['label'], gap['predicate'].replace('_', ' '))

        else:
            say += ' Has %s %s a %s?' % (capsule['object']['label'], gap['predicate'].replace('_', ' '),
                                         gap['range'].replace('_', ' '))

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        say += ' What other %s %s %s?' % (gap['domain'].replace('_', ' '), gap['predicate'].replace('_', ' '),
                                   capsule['object']['label'])

    return say


def phrase_overlaps(overlaps, capsule):
    capsule = casefold_capsule(capsule, format='natural')

    if capsule['object']['type'] == '':
        capsule['object']['type'] = 'thing'

    if capsule['subject']['type'] == '':
        capsule['subject']['type'] = 'thing'

    entity_role = random.choice(overlaps.keys())

    if not overlaps[entity_role] and entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' I did not know anybody who %s %s' % (capsule['predicate']['type'], capsule['object']['label'])

    elif not overlaps[entity_role] and entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' I did not know anybody who %s %s' %(capsule['predicate']['type'], capsule['object']['label'])

    elif entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' Now I know that %s %s %s %s' % (capsule['subject']['label'], capsule['predicate']['type'],
                                                 len(overlaps[entity_role]), capsule['object']['type'])

    elif entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' Now I know %s %s that %s %s' %(len(overlaps[entity_role]), capsule['subject']['type'],
                                                capsule['predicate']['type'], capsule['object']['label'])

    return say


def phrase_trust(trust):
    if trust == 1:
        say = random.choice(TRUST)
    else:
        say = random.choice(NO_TRUST)

    return say


def phrase_update(update, proactive=False, persist=False):
    options = ['cardinality_conflicts', 'negation_conflicts', 'statement_novelty', 'entity_novelty']

    if proactive:
        options.extend(['subject_gaps', 'object_gaps', 'overlaps'])

    approach = random.choice(options)

    if approach == 'cardinality_conflicts':
        say = phrase_cardinality_conflicts(update['cardinality_conflicts'], update['statement'])

    elif approach == 'negation_conflicts':
        say = phrase_negation_conflicts(update['negation_conflicts'], update['statement'])

    elif approach == 'statement_novelty':
        say = phrase_statement_novelty(update['statement_novelty'])

    elif approach == 'entity_novelty':
        say = phrase_type_novelty(update['entity_novelty'], update['statement'])

    elif approach == 'subject_gaps':
        say = phrase_subject_gaps(update['subject_gaps'], update['statement'])

    elif approach == 'object_gaps':
        say = phrase_object_gaps(update['object_gaps'], update['statement'])

    elif approach == 'overlaps':
        say = phrase_overlaps(update['overlaps'], update['statement'])

    if persist and say == '':
        say = phrase_update(update, proactive, persist)

    return say
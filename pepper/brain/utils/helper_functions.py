import os
import random
from datetime import datetime

from pepper.knowledge.sentences import NEW_KNOWLEDGE, EXISTING_KNWOLEDGE, CONFLICTING_KNOWLEDGE, CURIOSITY, HAPPY, \
    TRUST, NO_TRUST


def read_query(query_filename):
    with open(os.path.join(os.path.dirname(__file__), "../queries/{}.rq".format(query_filename))) as fr:
        query = fr.read()
    return query


def casefold(text):
    return text.lower().replace(" ", "_") if isinstance(text, basestring) else text


def casefold_capsule(capsule):
    for k, v in capsule.items():
        if isinstance(v, dict):
            capsule[k] = casefold_capsule(v)
        else:
            capsule[k] = casefold(v)

    return capsule


def hash_statement_id(triple, debug=False):
    if debug:
        print('This is the triple: {}'.format(triple))
    temp = '-'.join(triple)

    return temp


# TODO to be moved to NLP layer
def phrase_all_conflicts(conflicts):
    say = 'I have %s conflicts in my brain.' % len(conflicts)

    conflict = random.choice(conflicts)

    # Conflict of subject
    if len(conflict['objects']) > 1:
        options = ['%s %s like %s told me' % (conflict['predicate'].replace('_', ' '), item['value'], item['author']) for item in conflict['objects']]
        options = ' or '.join(options)
        subject = 'I' if conflict['subject'] == 'Leolani' else conflict['subject']

        say = say + ' For example, I do not know if %s %s %s'% (subject, conflict['predicate'].replace('_', ' '), options)

    return say


def phrase_cardinality_conflicts(conflict, capsule):
    # There is no conflict, so nothing to say
    if conflict[0] == {}:
        say = ''

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)
        conflict = random.choice(conflict)
        x = 'you' if conflict['authorlabel']==capsule['author'] else conflict['authorlabel']

        y = 'you' if capsule['subject']['label']==conflict['authorlabel'] else capsule['subject']['label']

        say += ' %s told me in %s that %s %s %s, but now you tell me that %s %s %s' \
               % (x,
                  datetime.strptime(conflict['date'], "%Y-%m-%d").strftime("%B"),
                  y.replace('_', ' '), capsule['predicate']['type'].replace('_', ' '),
                  conflict['oname'].replace('_', ' '),
                  y.replace('_', ' '), capsule['predicate']['type'].replace('_', ' '),
                  capsule['object']['label'].replace('_', ' '))

    return say


def phrase_negation_conflicts(conflict, capsule):
    # There is no conflict, so nothing to say
    if conflict == {}:
        say = ''

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)

        say += ' %s told me in %s that %s %s %s, but in %s %s told me that %s did not %s %s' \
            %(conflict['positive']['authorlabel'].replace('_', ' '),
              datetime.strptime(conflict['positive']['date'], "%Y-%m-%d").strftime("%B"),
              capsule['subject']['label'].replace('_', ' '), capsule['predicate']['type'].replace('_', ' '),
              capsule['object']['label'].replace('_', ' '),
              datetime.strptime(conflict['negative']['date'], "%Y-%m-%d").strftime("%B"),
              conflict['negative']['authorlabel'].replace('_', ' '),
              capsule['subject']['label'].replace('_', ' '), capsule['predicate']['type'].replace('_', ' '),
              capsule['object']['label'].replace('_', ' '))

    return say


def phrase_statement_novelty(novelty):
    # I do not know this before
    if novelty[0] == {}:
        say = random.choice(NEW_KNOWLEDGE)

    # I already knew this
    else:
        say = random.choice(EXISTING_KNWOLEDGE)
        provenance = random.choice(novelty)

        say += ' %s told me about it in %s' %(provenance['authorlabel'].replace('_', ' '),
                                                datetime.strptime(provenance['date'], "%Y-%m-%d").strftime("%B"))

    return say


def phrase_type_novelty(novelty, capsule):
    entity_role = random.choice(novelty.keys())

    if novelty[entity_role]:
        say = random.choice(NEW_KNOWLEDGE)
        say += ' I have never heard about %s before!' % capsule[entity_role]['label'].replace('_', ' ')

    else:
        say = random.choice(EXISTING_KNWOLEDGE)
        say += ' I know about %s.' % capsule[entity_role]['label'].replace('_', ' ')

    return say


def phrase_subject_gaps(gaps, capsule):
    entity_role = random.choice(gaps.keys())

    if not gaps[entity_role]:
        say = ''

    elif entity_role == 'subject':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        if '#' in gap['range']:
            say += ' What is %s %s' % (capsule['subject']['label'].replace('_', ' '), gap['predicate'].replace('_', ' '))

        else:
            say += ' Has %s %s a %s?' %(capsule['subject']['label'].replace('_', ' '),
                                       gap['predicate'].replace('_', ' '), gap['range'].replace('_', ' '))

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        say += ' Is there a %s %s %s?' % (gap['domain'].replace('_', ' '), gap['predicate'].replace('_', ' '),
                                        capsule['subject']['label'].replace('_', ' '))

    return say


def phrase_object_gaps(gaps, capsule):
    entity_role = random.choice(gaps.keys())

    if not gaps[entity_role]:
        say = ''

    elif entity_role == 'subject':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        if '#' in gap['range']:
            say += ' What is %s %s' % (capsule['object']['label'].replace('_', ' '), gap['predicate'].replace('_', ' '))

        else:
            say += ' Has %s %s a %s?' % (capsule['object']['label'].replace('_', ' '),
                                       gap['predicate'].replace('_', ' '), gap['range'].replace('_', ' '))

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)
        gap = random.choice(gaps[entity_role])

        say += ' What other %s %s %s?' % (gap['domain'].replace('_', ' '), gap['predicate'].replace('_', ' '),
                                   capsule['object']['label'].replace('_', ' '))

    return say


def phrase_overlaps(overlaps, capsule):
    if capsule['object']['type'].replace('_', ' ') == '':
        capsule['object']['type'] = 'thing'

    if capsule['subject']['type'].replace('_', ' ') == '':
        capsule['subject']['type'] = 'thing'

    entity_role = random.choice(overlaps.keys())

    if not overlaps[entity_role] and entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' I did not know anybody who %s %s' % (capsule['predicate']['type'].replace('_', ' '),
                                                      capsule['object']['label'].replace('_', ' '))

    elif not overlaps[entity_role] and entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' I did not know anybody who %s %s' %(capsule['predicate']['type'].replace('_', ' '),
                                                    capsule['object']['label'].replace('_', ' '))

    elif entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' Now I know that %s %s %s %s' % (capsule['subject']['label'].replace('_', ' '),
                                                 capsule['predicate']['type'].replace('_', ' '),
                                                 len(overlaps[entity_role]),
                                                 capsule['object']['type'].replace('_', ' '))

    elif entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' Now I know %s %s that %s %s' %(len(overlaps[entity_role]),
                                                capsule['subject']['type'].replace('_', ' '),
                                                capsule['predicate']['type'].replace('_', ' '),
                                                capsule['object']['label'].replace('_', ' '))

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
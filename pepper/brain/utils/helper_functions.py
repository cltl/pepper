import os
import random
from datetime import datetime

from pepper.knowledge.sentences import NEW_KNOWLEDGE, EXISTING_KNWOLEDGE, CONFLICTING_KNOWLEDGE


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

        say += ' %s told me in %s that %s %s %s, but now you tell me that %s %s %s' \
               % (conflict['authorlabel'],
                  datetime.strptime(conflict['date'], "%Y-%m-%d").strftime("%B"),
                  capsule['subject']['label'], capsule['predicate']['type'].replace('_', ' '), conflict['oname'],
                  capsule['subject']['label'], capsule['predicate']['type'].replace('_', ' '), capsule['object']['label'])

    return say


def phrase_negation_conflicts(conflict, capsule):
    # There is no conflict, so nothing to say
    if conflict['positive'] == {} or conflict['negative'] == {}:
        say = ''

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)

        say += ' %s told me in %s that %s %s %s, but in %s %s told me that %s did not %s %s' \
            %(conflict['positive']['authorlabel'],
              datetime.strptime(conflict['positive']['date'], "%Y-%m-%d").strftime("%B"),
              capsule['subject']['label'], capsule['predicate']['type'].replace('_', ' '), capsule['object']['label'],
              datetime.strptime(conflict['negative']['date'], "%Y-%m-%d").strftime("%B"),
              conflict['negative']['authorlabel'],
              capsule['subject']['label'], capsule['predicate']['type'].replace('_', ' '), capsule['object']['label'])

    return say


def phrase_statement_novelty(novelty):
    # I do not know this before
    if novelty[0] == {}:
        say = random.choice(NEW_KNOWLEDGE)

    # I already knew this
    else:
        say = random.choice(EXISTING_KNWOLEDGE)
        provenance = random.choice(novelty)

        say += ' %s told me about it in %s' %(provenance['authorlabel'],
                                                datetime.strptime(provenance['date'], "%Y-%m-%d").strftime("%B"))

    return say


def phrase_type_novelty(novelty, capsule):
    entity_role = random.choice(novelty.keys())

    if not novelty[entity_role]:
        say = 'I have never heard about %s before! I am glad to have learned something new.' % capsule[entity_role]['label']

    else:
        say = 'I know about %s.' % capsule[entity_role]['label']

    return say


def phrase_update(update):
    approach = random.choice(['cardinality_conflicts', 'negation_conflicts', 'statement_novelty', 'entity_novelty'])

    if approach == 'cardinality_conflicts':
        say = phrase_cardinality_conflicts(update['cardinality_conflicts'], update['statement'])

    elif approach == 'negation_conflicts':
        say = phrase_negation_conflicts(update['negation_conflicts'], update['statement'])

    elif approach == 'statement_novelty':
        say = phrase_statement_novelty(update['statement_novelty'])

    elif approach == 'entity_novelty':
        say = phrase_type_novelty(update['entity_novelty'], update['statement'])

    return say
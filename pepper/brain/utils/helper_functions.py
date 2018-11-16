import os
import random
from datetime import datetime


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
        options = ['%s like %s told me' % (item['value'], item['author']) for item in conflict['objects']]
        options = ' or '.join(options)
        predicate = conflict['predicate'].replace('_', ' ')
        subject = 'I' if conflict['subject'] == 'Leolani' else conflict['subject']

        say = say + ' For example, I do not know if %s %s %s'% (subject, predicate, options)

    return say


def phrase_negation_conflicts(conflict):
    say = 'I am surprised. '

    say += '%s told me in %s that %s %s %s, but in %s %s told me that %s did not' \
        %(conflict['positive']['authorlabel'], datetime.strptime(conflict['positive']['date'], "%Y-%m-%d").strftime("%B"),
          conflict['capsule']['subject']['label'], conflict['capsule']['predicate']['type'], conflict['capsule']['object']['label'],
          datetime.strptime(conflict['negative']['date'], "%Y-%m-%d").strftime("%B"), conflict['negative']['authorlabel'], conflict['capsule']['subject']['label'])

    return say


def sensor_info():
    # try coco first, else try imagenet
    # if web recognizes, then
    # create triples of sensor
    # phrase what I have seen (I see a fridge, which is choice type or description)
    # if web does not recognize, say idk
    # maybe ask type and store
    pass
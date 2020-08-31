import random

from pepper.language.generation.phrasing import *
from pepper.language.utils.helper_functions import lexicon_lookup


def assign_spo(utterance, item):
    # INITIALIZATION
    predicate = utterance.triple.predicate_name

    if utterance.triple.subject_name != '':
        subject = utterance.triple.subject_name
    else:
        subject = item['slabel']['value']

    if utterance.triple.complement_name != '':
        object = utterance.triple.complement_name
    elif 'olabel' in item:
        object = item['olabel']['value']
    else:
        object = ''

    return subject, predicate, object


def deal_with_authors(author, previous_author, predicate, previous_predicate, say):
    # Deal with author
    if author != previous_author:
        say += author + ' told me '
        previous_author = author
    else:
        if predicate != previous_predicate:
            say += ' that '

    return say, previous_author


def fix_entity(entity, speaker):
    new_ent = ''
    if '-' in entity:
        entity_tokens = entity.split('-')

        for word in entity_tokens:
            new_ent += replace_pronouns(speaker, entity_label=word, role='pos') + ' '

    else:
        new_ent += replace_pronouns(speaker, entity_label=entity)

    entity = new_ent
    return entity


def reply_to_question(brain_response):
    say = ''
    previous_author = ''
    previous_predicate = ''
    gram_person = ''
    gram_number = ''

    utterance = brain_response['question']
    response = brain_response['response']

    # TODO revise by Lenka (we conjugate the predicate by doing this)
    utterance.casefold(format='natural')

    if not response:
        if utterance.triple.subject.types and utterance.triple.complement.types and utterance.triple.predicate_name:
            say += "I know %s usually %s %s, but I do not know this case" % (
                random.choice(utterance.triple.subject.types), str(utterance.triple.predicate_name),
                random.choice(utterance.triple.complement.types))
            return say

        else:
            return None

    # Each triple is hashed, so we can figure out when we are about the say things double
    handled_items = set()
    response.sort(key=lambda x: x['authorlabel']['value'])

    for item in response:

        # INITIALIZATION
        subject, predicate, object = assign_spo(utterance, item)

        author = replace_pronouns(utterance.chat_speaker, author=item['authorlabel']['value'])
        subject = replace_pronouns(utterance.chat_speaker, entity_label=subject, role='subject')
        object = replace_pronouns(utterance.chat_speaker, entity_label=object, role='object')

        fixed_subject = fix_entity(subject, utterance.chat_speaker)
        fixed_object = fix_entity(object, utterance.chat_speaker)

        # Hash item such that duplicate entries have the same hash
        item_hash = '{}_{}_{}_{}'.format(subject, predicate, object, author)

        # If this hash is already in handled items -> skip this item and move to the next one
        if item_hash in handled_items:
            continue
        # Otherwise, add this item to the handled items (and handle item the usual way (with the code below))
        else:
            handled_items.add(item_hash)

        # Get grammatical properties
        subject_entry = lexicon_lookup(subject.lower())
        if subject_entry and 'person' in subject_entry:
            gram_person = subject_entry['person']
        if subject_entry and 'number' in subject_entry:
            gram_number = subject_entry['number']

        # Deal with author
        say, previous_author = deal_with_authors(author, previous_author, predicate, previous_predicate, say)

        if predicate.endswith('is'):

            say += object + ' is'
            if utterance.triple.complement_name.lower() == utterance.chat_speaker.lower() or \
                    utterance.triple.subject_name.lower() == utterance.chat_speaker.lower():
                say += ' your '
            elif utterance.triple.complement_name.lower() == 'leolani' or \
                    utterance.triple.subject_name.lower() == 'leolani':
                say += ' my '
            say += predicate[:-3]

            return say

        else:  # TODO fix_predicate_morphology
            be = {'first': 'am', 'second': 'are', 'third': 'is'}
            if predicate == 'be':  # or third person singular
                if gram_number:
                    if gram_number == 'singular':
                        predicate = be[gram_person]
                    else:
                        predicate = 'are'
                else:
                    # TODO: Is this a good default when 'number' is unknown?
                    predicate = 'is'
            elif gram_person == 'third' and not '-' in predicate:
                predicate += 's'

            if item['certaintyValue']['value'] != 'CERTAIN':  # TODO extract correct certainty marker
                predicate = 'maybe ' + predicate

            if item['polarityValue']['value'] != 'POSITIVE':
                if ' ' in predicate:
                    predicate = predicate.split()[0] + ' not ' + predicate.split()[1]
                else:
                    predicate = 'do not ' + predicate

            say += subject + ' ' + predicate + ' ' + object

        say += ' and '

    say = say[:-5]

    return say.replace('-', ' ').replace('  ', ' ')

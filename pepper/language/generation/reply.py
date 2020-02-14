import random

from pepper.language.generation.phrasing import *
from pepper.language.utils.helper_functions import wnl, lexicon_lookup


def fix_predicate_morphology(subject, predicate, object, format='triple'):
    """
    Conjugation
    Parameters
    ----------
    subject
    predicate

    Returns
    -------

    """
    new_predicate = ''
    if format == 'triple':
        if len(predicate.split()) > 1:
            for el in predicate.split():
                if el == 'is':
                    new_predicate += 'be-'
                else:
                    new_predicate += el + '-'

        elif predicate.endswith('s'):
            new_predicate = wnl.lemmatize(predicate)

        else:
            new_predicate = predicate

    elif format == 'natural':
        if len(predicate.split()) > 1:
            for el in predicate.split():
                if el == 'be':
                    new_predicate += 'is '
                else:
                    new_predicate += el + ' '

        # elif predicate == wnl.lemmatize(predicate):
        #    new_predicate = predicate + 's'

        else:
            new_predicate = predicate

    return new_predicate.strip(' ')


def reply_to_question(brain_response):
    say = ''
    previous_author = ''
    previous_subject = ''
    previous_predicate = ''
    person = ''

    utterance = brain_response['question']
    response = brain_response['response']


    # TODO revise by Lenka (we conjugate the predicate by doing this)
    utterance.casefold(format='natural')

    if not response:
        # TODO revise by lenka (we catch responses we could have known here)
        subject_type = random.choice(utterance.triple.subject.types) if utterance.triple.subject.types else 'things'
        object_type = random.choice(
            utterance.triple.complement.types) if utterance.triple.complement.types else 'things'
        predicate = str(utterance.triple.predicate_name)
        say += "I know %s usually %s %s, but I do not know this case" % (subject_type, predicate, object_type)
        return say

    '''
    if utterance.triple.predicate_name == 'sees' and utterance.triple.subject_name == 'leolani':
        print(viewed_objects)
        say = 'I see '
        for obj in viewed_objects:
            if len(viewed_objects)>1 and obj == viewed_objects[len(viewed_objects)-1]:
                say += ', and a '+obj
            else:
                say+=' a '+obj+', '

        if utterance.triple.complement_name:
            if utterance.triple.complement_name.lower() in viewed_objects:
                say = 'yes, I can see a ' + utterance.triple.complement_name
            else:
                say = 'no, I cannot see a ' + utterance.triple.complement_name
    '''

    response.sort(key=lambda x: x['authorlabel']['value'])

    # TODO: Bram: Quick solution for duplicate Brain items
    # Each (subject, predicate, object, author) tuple is hashed,
    # So we can figure out when we are about the say things double
    handled_items = set()

    for item in response:

        # INITIALIZATION
        author = replace_pronouns(utterance.chat_speaker, author=item['authorlabel']['value'])
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

        predicate = utterance.triple.predicate_name

        subject = replace_pronouns(utterance.chat_speaker, entity_label=subject, role='subject')

        # TODO: Bram: Quick solution for duplicate Brain items
        # Hash item such that duplicate entries have the same hash
        item_hash = '{}_{}_{}_{}'.format(subject, predicate, object, author)

        # If this hash is already in handled items -> skip this item and move to the next one
        if item_hash in handled_items: continue

        # Otherwise, add this item to the handled items (and handle item the usual way (with the code below))
        else: handled_items.add(item_hash)

        '''
        new_sub = replace_pronouns(utterance.chat_speaker, entity_label=subject, role='subject')

        if utterance.transcript.split()[0].lower()!='who' or new_sub.lower() in ['i','you']:
            subject = new_sub
        '''

        if '-' in subject:
            new_sub = ''
            for word in subject.split('-'):
                new_sub += replace_pronouns(utterance.chat_speaker, entity_label=word, role='pos') + ' '
            subject = new_sub

        subject_entry = lexicon_lookup(subject.lower())

        if subject_entry and 'person' in subject_entry:
            person = subject_entry['person']

        # Deal with author
        if author != previous_author:
            say += author + ' told me '
            previous_author = author
        else:
            if predicate != previous_predicate:
                say += ' that '

        if item['sentimentValue']['value']!='UNDERSPECIFIED':
            print('sentiment', item['sentimentValue']['value'])


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
                if subject_entry and 'number' in subject_entry:
                    if subject_entry['number'] == 'singular':
                        predicate = be[person]
                    else:
                        predicate = 'are'
                else:
                    # TODO: Bram: Is this a good default when 'number' is unknown?
                    predicate = 'is'
            elif person == 'third' and not '-' in predicate:
                predicate += 's'

            if item['certaintyValue']['value'] != 'CERTAIN': #TODO extract correct certainty marker
                print('certainty', item['certaintyValue']['value'])
                predicate = 'maybe '+predicate

            if item['polarityValue']['value'] != 'POSITIVE':
                print('polarity', item['polarityValue']['value'], predicate)
                if ' ' in predicate:
                    predicate = predicate.split()[0]+ ' not '+predicate.split()[1]
                else:
                    predicate = 'do not '+predicate

            say += subject + ' ' + predicate + ' ' + object

        say += ' and '

    return say[:-5]

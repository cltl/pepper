import random

from pepper.language.generation.phrasing import *
from pepper.language.utils.helper_functions import wnl


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
    # TODO revise by Lenka
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

        #elif predicate == wnl.lemmatize(predicate):
        #    new_predicate = predicate + 's'

        else:
            new_predicate = predicate

    return new_predicate.strip(' ')


def reply_to_statement(template, speaker, brain, viewed_objects=[]):
    subject = template['statement'].triple.subject_name
    predicate = template['statement'].triple.predicate_name
    object = template['statement'].triple.object_name

    if predicate == 'isFrom': predicate = 'is from'

    if (speaker.lower() in [subject.lower(), 'speaker'] or subject == 'Speaker'):
        subject = 'you '
    else:
        if subject.lower() == 'leolani':
            subject = 'i'
        else:
            subject.title()

    if subject == 'you ':
        predicate = fix_predicate_morphology(predicate, format='natural')

    if subject == 'i' and predicate.endswith('s'): predicate = predicate[:-1]

    if object.lower() == speaker.lower(): object = 'you'

    response = subject + ' ' + predicate + ' ' + object

    print("INITIAL RESPONSE ", response)

    if predicate == 'own':
        response = subject + ' ' + predicate + ' a ' + object

    if predicate in ['see', 'sees']:

        response = subject + ' ' + predicate + ' a ' + object

        if object.lower() in viewed_objects:
            response += ', I see a ' + object + ', too!'
        else:
            response += ', but I don\'t see it!'

        class_recognized, text = brain.reason_entity_type(object)

        if class_recognized is not None:
            capsule = {
                "subject": {
                    "label": "",
                    "type": ""
                },
                "predicate": {
                    "type": ""
                },
                "object": {
                    "label": "apple",
                    "type": class_recognized
                },
                "author": "front_camera",
                "chat": None,
                "turn": None,
                "position": "0-15-0-15",
                "date": date.today()
            }

            brain.experience(capsule)

        response += text

    elif predicate.strip() == 'see-not':
        response = 'You don\'t see a ' + object
        if object.lower() in viewed_objects:
            response += ', but I see it'
        else:
            response += ', and I also don\'t see it'

    return response


def reply_to_question(brain_response):
    say = ''
    previous_author = ''
    previous_subject = ''
    previous_predicate = ''

    utterance = brain_response['question']
    response = brain_response['response']

    # TODO revise by Lenka (we conjugate the predicate by doing this)
    utterance.casefold(format='natural')

    if not response:
        # TODO revise by lenka (we catch responses we could have known here)
        subject_type = random.choice(utterance.triple.subject.types) if utterance.triple.subject.types else 'things'
        object_type = random.choice(utterance.triple.object.types) if utterance.triple.object.types else 'things'
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

        if utterance.triple.object_name:
            if utterance.triple.object_name.lower() in viewed_objects:
                say = 'yes, I can see a ' + utterance.triple.object_name
            else:
                say = 'no, I cannot see a ' + utterance.triple.object_name
    '''

    response.sort(key=lambda x: x['authorlabel']['value'])

    for item in response[:4]:
        # print(response)
        author = replace_pronouns(utterance.chat_speaker, author=item['authorlabel']['value'])
        if brain_response['question'].transcript.split()[0].lower()!='who':
            subject = replace_pronouns(utterance.chat_speaker, entity_label=utterance.triple.subject_name, role='subject')
        else:
            #print(item)
            if utterance.triple.subject_name!='':
                subject = utterance.triple.subject_name
            else:
                subject = item['slabel']['value']

        predicate = utterance.triple.predicate_name
        person = ''

        # Deal with author
        if author != previous_author:
            say += author + ' told me '
            previous_author = author

        elif author == previous_author:
            if predicate != previous_predicate:
                say += ' that '

        # Deal with normal predicates attributes like can, read, etc
        if not predicate.endswith('is'):
            # Deal with answers to who can fly for example
            if 'slabel' in item:
                #slabel = replace_pronouns(utterance.chat_speaker, entity_label=item['slabel']['value'], role='subject')
                slabel = item['slabel']['value']
                if slabel == 'you':
                    person = 'second'
                elif slabel == 'I':
                    person = 'first'

                elif (item['slabel']['value'].lower() == previous_subject.lower()) or (
                        item['slabel']['value'].lower() == item['authorlabel']['value'].lower()):
                    print('maybe error here')

                else:
                    previous_subject = item['slabel']['value'].lower()
                say += slabel
            else:
                say+= subject

        # Deal with attribute predicates like favorite-is, mom-is, etc
        else:
            if 'olabel' in item:
                say += item['olabel']['value']
            elif 'slabel' in item:
                say += item['slabel']['value']

        #
        '''
        if subject.lower() != previous_subject.lower():
            if subject == 'you':
                person = 'second'
            elif subject == 'I':
                person = 'first'
            say += ' {} '.format(subject)
            previous_subject = subject
        '''

        # if predicate in grammar['predicates']:
        if predicate == previous_predicate:  # and response['slabel'].lower()==previous_subject.lower():
            say+= ' '+predicate+' '
        else:
            previous_predicate = predicate
            if predicate == 'see':
                say += ' saw'
            elif predicate == 'be-from':
                if person == 'first':
                    say += ' am from '
                elif person == 'second':
                    say += ' are from '
                else:
                    say += ' is from '

            elif predicate.endswith('is'):
                #print('ODJE SAM')
                say += ' is '
                print(utterance.triple.object_name.lower())
                if utterance.triple.object_name.lower() == utterance.chat_speaker.lower() or \
                        utterance.triple.subject_name.lower() == utterance.chat_speaker.lower():
                    say += ' your '
                elif utterance.triple.object_name.lower() == 'leolani' or \
                        utterance.triple.subject_name.lower() == 'leolani':
                    say += ' my '
                say += predicate[:-3]

                return say

            elif subject.strip() in ['he','she'] and len(predicate.split())==1:
                say+= ' '+predicate+'s '

            else:
                say += ' ' + predicate + ' '

        if 'olabel' in item:
            say += item['olabel']['value']

        if utterance.triple.object_name.lower() == utterance.chat_speaker.lower():
            say += ' you'
        elif utterance.triple.object_name.lower() == 'leolani':
            say += ' me'

        else:
            say += utterance.triple.object_name

        '''
                elif predicate.lower() in ['see', 'own']:
            say += ' a ' + utterance.triple.object_name
        '''

        say += ' and '

    return say[:-5]

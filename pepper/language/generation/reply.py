from pepper.language.generation.phrasing import *


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
        predicate = fix_predicate_morphology(predicate)

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

        class_recognized, text = brain.process_visual(object)

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

    elif predicate.strip() == 'sees-not':
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

    '''
    if utterance.triple.predicate_name == 'sees' and utterance.triple.subject_label == 'leolani':
        print(viewed_objects)
        say = 'I see '
        for obj in viewed_objects:
            if len(viewed_objects)>1 and obj == viewed_objects[len(viewed_objects)-1]:
                say += ', and a '+obj
            else:
                say+=' a '+obj+', '

        if utterance.triple.object_label:
            if utterance.triple.object_label.lower() in viewed_objects:
                say = 'yes, I can see a ' + utterance.triple.object_label
            else:
                say = 'no, I cannot see a ' + utterance.triple.object_label
    '''

    response.sort(key=lambda x: x['authorlabel']['value'])

    for item in response[:4]:
        author = replace_pronouns(utterance.chat_speaker, author=item['authorlabel']['value'])
        subject = replace_pronouns(utterance.chat_speaker, entity_label=utterance.triple.subject_name, role='subject')
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
        if not predicate.endswith('-is'):
            # Deal with answers to who can fly for example
            if 'slabel' in item:
                slabel = replace_pronouns(utterance.chat_speaker, entity_label=item['slabel']['value'], role='subject')
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

        # Deal with attribute predicates like favorite-is, mom-is, etc
        else:
            if 'olabel' in item:
                say += item['olabel']['value']
            elif 'slabel' in item:
                say += item['slabel']['value']

        #
        if subject.lower() != previous_subject.lower():
            if subject == 'you':
                person = 'second'
            elif subject == 'I':
                person = 'first'
            say += ' {} '.format(subject)
            previous_subject = subject

        # if predicate in grammar['predicates']:
        if predicate == previous_predicate:  # and response['slabel'].lower()==previous_subject.lower():
            pass
        else:
            previous_predicate = predicate
            if predicate == 'sees':
                say += ' saw'
            elif predicate == 'be-from':
                if person == 'first':
                    say += ' am from '
                elif person == 'second':
                    say += ' are from '
                else:
                    say += ' is from '

            elif predicate.endswith('-is'):
                say += ' is '
                print(utterance.triple.object_label.lower())
                if utterance.triple.object_label.lower() == utterance.chat_speaker.lower() or \
                        utterance.triple.subject_label.lower() == utterance.chat_speaker.lower():
                    say += ' your '
                elif utterance.triple.object_label.lower() == 'leolani' or \
                        utterance.triple.subject_label.lower() == 'leolani':
                    say += ' my '
                say += predicate[:-3]

                return say


            else:
                if person in ['first', 'second'] and predicate.endswith('s'):
                    say += ' ' + predicate[:-1] + ' '
                else:
                    say += ' ' + predicate + ' '

        if 'olabel' in item:
            say += item['olabel']['value']
        elif 'object' in utterance.keys():
            if utterance.triple.object_label.lower() == utterance.chat_speaker.lower():
                say += ' you'
            elif utterance.triple.object_label.lower() == 'leolani':
                say += ' me'
            elif predicate.lower() in ['sees', 'owns']:
                say += ' a ' + utterance.triple.object_label
            else:
                say += utterance.triple.object_label

        say += ' and '

    return say[:-5]


def fix_predicate_morphology(subject, predicate):
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
    for el in predicate.split():
        if el != 'is':
            new_predicate += el + ' '
        else:
            new_predicate += 'are '

    if predicate.endswith('s'): new_predicate = predicate[:-1]

    return new_predicate


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


def reply_to_question(brain_response, viewed_objects=[]):
    say = ''
    previous_author = ''
    previous_subject = ''
    previous_predicate = ''

    '''
    if 'hack' not in brain_response['question']['object'] and (len(brain_response['response'])==0 or brain_response['question']['predicate']['type'] == 'sees'): #FIX
        if brain_response['question']['predicate']['type'] == 'sees' and brain_response['question']['subject']['label'] == 'leolani':
            print(viewed_objects)
            say = 'I see '
            for obj in viewed_objects:
                if len(viewed_objects)>1 and obj == viewed_objects[len(viewed_objects)-1]:
                    say += ', and a '+obj
                else:
                    say+=' a '+obj+', '

            if brain_response['question']['object']['label']:
                if brain_response['question']['object']['label'].lower() in viewed_objects:
                    say = 'yes, I can see a ' + brain_response['question']['object']['label']
                else:
                    say = 'no, I cannot see a ' + brain_response['question']['object']['label']

        else:
            return None
        return say+'\n'
    '''

    brain_response['response'].sort(key=lambda x: x['authorlabel']['value'])

    previous_response = ''
    for response in brain_response['response'][:4]:

        # avoid repetition?
        if response == previous_response:
            break
        else:
            previous_response = response

        person = ''
        if 'authorlabel' in response and response['authorlabel']['value'] != previous_author:
            if response['authorlabel']['value'].lower() == brain_response['question']['author'].lower():
                say += ' you told me '
            else:
                say += response['authorlabel']['value'] + ' told me '
            previous_author = response['authorlabel']['value'].lower()
        elif 'authorlabel' in response and response['authorlabel']['value'].lower() == previous_author:
            if brain_response['question']['predicate']['type'] != previous_predicate:
                say += ' that '

        print('response', response)

        if not brain_response['question']['predicate']['type'].endswith('-is'):

            if 'slabel' in response:
                if response['slabel']['value'].lower() == brain_response['question']['author'].lower():
                    say += 'you'
                    person = 'second'
                elif response['slabel']['value'].lower() == 'leolani' and brain_response['question']['predicate'][
                                                                              'type'][-3:] != '-is':
                    say += 'I'
                    person = 'first'

                elif (response['slabel']['value'].lower() == previous_subject.lower()) or (
                        response['slabel']['value'].lower() == response['authorlabel']['value'].lower()):
                    if response['slabel']['value'].lower() in ['bram', 'piek']:
                        say += 'he'
                    elif response['slabel']['value'].lower() in ['selene', 'lenka']:
                        say += 'she'

                else:
                    say += response['slabel']['value'].lower()
                    previous_subject = response['slabel']['value'].lower()


        else:
            print('response', response)
            if 'olabel' in response:
                say += response['olabel']['value']
            elif 'slabel' in response:
                say += response['slabel']['value']

        if 'subject' in brain_response['question'] and brain_response['question']['subject'][
            'label'].lower() != previous_subject.lower():
            if brain_response['question']['subject']['label'].lower() == brain_response['question']['author'].lower():
                person = 'second'
                say += ' you '
            elif brain_response['question']['subject']['label'].lower() == 'leolani':
                say += ' I '
                person = 'first'
            else:
                say += brain_response['question']['subject']['label'].lower()
            previous_subject = brain_response['question']['subject']['label'].lower()

        # if brain_response['question']['predicate']['type'] in grammar['predicates']:
        if brain_response['question']['predicate'][
            'type'] == previous_predicate:  # and response['slabel'].lower()==previous_subject.lower():
            pass
        else:
            previous_predicate = brain_response['question']['predicate']['type']
            if brain_response['question']['predicate']['type'] == 'sees':
                say += ' saw'
            elif brain_response['question']['predicate']['type'] == 'be-from':
                if person == 'first':
                    say += ' am from '
                elif person == 'second':
                    say += ' are from '
                else:
                    say += ' is from '

            elif brain_response['question']['predicate']['type'].endswith('-is'):
                say += ' is '
                print(brain_response['question']['object']['label'].lower())
                if brain_response['question']['object']['label'].lower() == brain_response['question'][
                    'author'].lower() or \
                        brain_response['question']['subject']['label'].lower() == brain_response['question'][
                    'author'].lower():
                    say += ' your '
                elif brain_response['question']['object']['label'].lower() == 'leolani' or \
                        brain_response['question']['subject']['label'].lower() == 'leolani':
                    say += ' my '
                say += brain_response['question']['predicate']['type'][:-3]

                return say


            else:
                if person in ['first', 'second'] and brain_response['question']['predicate']['type'].endswith('s'):
                    say += ' ' + brain_response['question']['predicate']['type'][:-1] + ' '
                else:
                    say += ' ' + brain_response['question']['predicate']['type'] + ' '

        if 'olabel' in response:
            say += response['olabel']['value']
        elif 'object' in brain_response['question'].keys():
            if brain_response['question']['object']['label'].lower() == brain_response['question']['author'].lower():
                say += ' you'
            elif brain_response['question']['object']['label'].lower() == 'leolani':
                say += ' me'
            elif brain_response['question']['predicate']['type'].lower() in ['sees', 'owns']:
                say += ' a ' + brain_response['question']['object']['label']
            else:
                say += brain_response['question']['object']['label']

        say += ' and '

    return say[:-5]

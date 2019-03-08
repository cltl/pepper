from __future__ import unicode_literals

from pepper import logger

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

from datetime import date
import random
import json
import re
import os
import analyzers_old


LOG = logger.getChild(__name__)


wnl = WordNetLemmatizer()

ROOT = os.path.join(os.path.dirname(__file__))
json_dict = json.load(open(os.path.join(ROOT, 'data', 'lexicon.json')))
grammar = json_dict

names = ['selene', 'bram', 'leolani', 'piek','selene', 'lenka']
statements = [['my favorite food is cake','lenka'],['I know Bram', 'Piek'],
              ['My name is lenka', 'person'],
               ['i like action movies', 'bram'],['bram likes romantic movies', 'selene'],
              ['bram is from Italy', 'selene']]  # [question, speaker]
questions = [['where is selene from?','jo'], ['what does piek like?', 'jo'], ['What is your name', 'person'], ['who knows bram?', 'ji'],
             ['who likes soccer?','selene'],
             ['who is from italy?','jill'], ['where are you from', 'person'], ['who do i know?', 'bram'],['where do you live?','person']]
             #['Have you ever met Michael Jordan?', 'piek'], ['Has Selene ever met piek', 'person'], ['Does Selene know piek', 'bram'],
             #['Does bram know Beyonce', 'person'], ['Do you know me','bram']]

def tokenize(utterance):
    '''
    This function returns a list of clean tokens, parsed from the inputted utterance
    '''
    words_raw = utterance.split()
    words = []
    for word in words_raw:
        clean_word = re.sub('[?!]', '', word)
        words.append(clean_word.lower())
    return words

def fix_contractions(words):
    '''
    If there are contractions (I'm) this functions creates the full version (I am)
    '''
    words.insert(1, words[0].split('\'')[1])
    words[0] = words[0].split('\'')[0]

    if words[1] == 'm': words[1] = 'am'
    if words[1] == 're': words[1] = 'are'
    if words[1] == 's': words[1] = 'is'

    return words


def get_synonims(word):
    '''
    Get synonyms using WordNet
    '''
    syns = wordnet.synsets(word)
    for s in syns:
        print(word+' - ' + s.lemmas()[0].name() + ': ' + s.definition())
        print(s.lemmas()[0].antonyms())

def extract_np(words, tagged, index):
    '''
    This function extracts a list of non-verbs (np = noun phrase)
    '''
    np = words[index]
    for pos in tagged[index+1:]:
        if (not pos[1].startswith('V') and (not pos[0] in ['like'])) or (pos[0] in names) :
            np += ' '+pos[0]
            index += 1
        else:
            break
    return np, index


def reply_to_question(brain_response, viewed_objects):

    say = ''
    previous_author = ''
    previous_subject = ''
    previous_predicate = ''

    # print(brain_response['question'])
    # print(brain_response['response'])

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

    brain_response['response'].sort(key=lambda x: x['authorlabel']['value'])
    # print(brain_response['response'])

    for response in brain_response['response'][:4]:
        person = ''
        if 'authorlabel' in response and response['authorlabel']['value']!=previous_author:
            if response['authorlabel']['value'].lower() == brain_response['question']['author'].lower():
                say+=' you told me '
            else:
                say += response['authorlabel']['value'] +' told me '
            previous_author = response['authorlabel']['value'].lower()
        elif 'authorlabel' in response and response['authorlabel']['value'].lower()==previous_author:
            if brain_response['question']['predicate']['type'] != previous_predicate:
                say+=' that '

        if 'slabel' in response:
            if response['slabel']['value'].lower()==brain_response['question']['author'].lower():
                say+= 'you'
                person = 'second'
            elif response['slabel']['value'].lower()=='leolani':
                say+='I'
                person='first'

            elif (response['slabel']['value'].lower() == previous_subject.lower()) or (response['slabel']['value'].lower() == response['authorlabel']['value'].lower()):
                if response['slabel']['value'].lower() in ['bram','piek']:
                    say+= 'he'
                elif response['slabel']['value'].lower() in ['selene','lenka']:
                    say+= 'she'

            else:
                say += response['slabel']['value'].lower()
                previous_subject = response['slabel']['value'].lower()

        elif 'subject' in brain_response['question'] and brain_response['question']['subject']['label'].lower() != previous_subject.lower():
            if brain_response['question']['subject']['label'].lower() == brain_response['question']['author'].lower():
                person = 'second'
                say+=' you '
            elif brain_response['question']['subject']['label'].lower() == 'leolani':
                say+=' I '
                person = 'first'
            else:
                say += brain_response['question']['subject']['label'].lower()
            previous_subject = brain_response['question']['subject']['label'].lower()

        #if brain_response['question']['predicate']['type'] in grammar['predicates']:
        if brain_response['question']['predicate']['type'] == previous_predicate: #and response['slabel'].lower()==previous_subject.lower():
            pass
        else:
            previous_predicate = brain_response['question']['predicate']['type']
            if brain_response['question']['predicate']['type'] == 'sees':
                say+=' saw'
            elif brain_response['question']['predicate']['type'] == 'is_from':
                if person == 'first':
                    say += ' am from '
                elif person == 'second':
                    say += ' are from'
                else:
                    say += ' is from '

            else:
                if person in ['first', 'second'] and brain_response['question']['predicate']['type'].endswith('s'):
                    say += ' ' + brain_response['question']['predicate']['type'][:-1] + ' '
                else:
                    say += ' '+brain_response['question']['predicate']['type']+' '

        if 'olabel' in response:
            say += response['olabel']['value']
        elif 'object' in brain_response['question'].keys():
            if brain_response['question']['object']['label'].lower()==brain_response['question']['author'].lower():
                say+='you'
            elif brain_response['question']['object']['label'].lower()=='leolani':
                say+='me'
            elif brain_response['question']['predicate']['type'].lower() in ['sees', 'owns']:
                say+=' a '+brain_response['question']['object']['label']
            else:
                say += brain_response['question']['object']['label']

        say+=' and '

    return say[:-5]

def write_template(speaker, rdf, chat_id, chat_turn, utterance_type):
    template = json.load(open(os.path.join(ROOT, 'data', 'template.json')))

    # print(template)

    template['author'] = speaker.title()
    template['utterance_type'] = utterance_type
    if type(rdf) == str:
        return rdf

    if not rdf:
        return 'error in the rdf'

    template['subject']['label'] = rdf['subject'].strip().lower() #capitalization
    template['subject']['type'] = "type.person"
    if rdf['predicate']=='seen':
        template['predicate']['type'] = 'sees'
        template['object']['hack'] = True
    else:
        template['predicate']['type'] = rdf['predicate'].strip()
    if rdf['object'] in names:
        template['object']['label'] = rdf['object'].strip()
        template['object']['type'] = 'PERSON'
    elif type(rdf['object']) is list:
        if rdf['object'][0] and rdf['object'][0].strip() in ['a', 'an', 'the']:
            rdf['object'].remove(rdf['object'][0])
        template['object']['label'] = rdf['object'][0].strip()
        if len(rdf['object'])>1: template['object']['type'] = rdf['object'][1]
    else:
        if rdf['object'].lower().startswith('a '):
            rdf['object'] = rdf['object'][2:]
        template['object']['label'] = rdf['object'].strip()
    template['date'] = date.today()
    template['chat'] = chat_id
    template['turn'] = chat_turn
    return template

def fix_predicate_morphology(predicate):
    new_predicate = ''
    for el in predicate.split():
        if el != 'is':
            new_predicate += el + ' '
        else:
            new_predicate += 'are '

    if predicate.endswith('s'): new_predicate = predicate[:-1]

    return new_predicate

def reply_to_statement(template, speaker, viewed_objects, brain):
    subject = template['statement']['subject']['label']
    predicate = template['statement']['predicate']['type']
    object = template['statement']['object']['label']

    if predicate == 'isFrom': predicate = 'is from'

    subject = 'you ' if (speaker.lower() in [subject.lower(),'speaker'] or subject=='Speaker') else 'i' if subject.lower()=='leolani' else subject.title()
    if subject=='you ':
        predicate = fix_predicate_morphology(predicate)

    if subject =='i' and predicate.endswith('s'): predicate = predicate[:-1]

    if object.lower() == speaker.lower(): object='you'


    response = subject +' '+predicate+' '+object

    print("INITIAL RESPONSE ", response)

    if predicate == 'own':
        response = subject+' '+predicate+' a '+object

    if predicate in ['see','sees']:

        response = subject+' '+predicate+' a '+object

        if object.lower() in viewed_objects:
            response+=', I see a '+object+', too!'
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
            response+= ', but I see it'
        else:
            response+= ', and I also don\'t see it'

    return response


def extract_roles_from_statement(words, speaker, viewed_objects):
    rdf = {'subject': '', 'predicate': '', 'object': ''}
    pos_list = pos_tag(words)
    i=0

    # OBJECT DETECTION SENTENCE
    if pos_list[0][0] in ['there', 'this', 'it', 'that']:
        if pos_list[1][0] in grammar['to be']:

            if pos_list[2][0] in grammar['possessive']:
                morph = analyzers_old.analyze_np(words[2:], speaker)
                #print(morph)
                if morph['predicate'].endswith('-is'):
                    rdf['predicate'] = 'owns'
                    rdf['object'] = morph['predicate'][:-3]
                    if morph['person'] == 'first': rdf['subject'] = speaker
                    elif morph['person']=='second': rdf['subject'] = 'leolani'
            else:
                rdf['subject']=speaker
                rdf['predicate']='sees'
                for word in words[2:]:
                    if word in ['no', 'not']:
                        rdf['predicate'] = 'sees-not'
                    elif word!='a': # does it matter which objects leolani sees?
                        rdf['object'] += (word + ' ')

    elif len(pos_list)>2 and pos_list[2][0] == 'see':
        if pos_list[1][0] =='can':
            rdf['predicate'] = 'sees'

        elif pos_list[1][0] in ['can\'t', 'cannot', 'don\'t']:
            rdf['predicate'] = 'sees-not'

        if pos_list[0][0].lower() == 'i':
            rdf['subject'] = speaker

        for word in words[3:]:
            if word!='a':
                rdf['object'] += (word + ' ')
    else:
        for pos in pos_list:
            if pos[1].startswith('V') or wnl.lemmatize(words[i]) in grammar['verbs']:
                if pos_list[i+1] and pos_list[i+1][0]=='from':
                    rdf['predicate'] = 'is_from'
                    i+=1
                else:
                    rdf['predicate'] = words[i]+'s'if not words[i].endswith('s') else words[i]
                    if rdf['predicate'] == 'cans': rdf['predicate'] = 'can'
                    if rdf['predicate'] == 'haves': rdf['predicate'] = 'owns'
                break
            rdf['subject']+=(words[i]+' ')
            i+= 1
        for word in words[i+1:]:
            rdf['object']+=(word+' ')
    return rdf


def check_rdf_completeness(rdf):
    for el in ['predicate', 'subject', 'object']:
        if not rdf[el] or not len(rdf[el]):
            LOG.warning("Cannot find {} in statement".format(el))
            return False
    '''    
    if rdf['predicate'] not in grammar['predicates'] and not rdf['predicate'].endswith('-not'):
        LOG.error('Nonexisting predicate: {}'.format(rdf['predicate']))
        return False
    '''

    return True

def pack_rdf_from_np_info(np_info, speaker, rdf):
    if 'object' in np_info.keys():
        rdf['object'] = np_info['object']
    if 'subject' in np_info.keys():
        rdf['subject'] = np_info['subject']
    if 'predicate' in np_info.keys():
        rdf['predicate'] = np_info['predicate']

    if 'human' in np_info.keys():
        rdf['subject'] = np_info['human']

    if 'entities' in np_info.keys():
        print(np_info['entities'])
        rdf['subject'] = np_info['entities']

    if 'pronoun' in np_info.keys() and 'person' in np_info['pronoun'].keys():
        rdf['subject'] = fix_pronouns(np_info['pronoun'], speaker)

    return rdf

def fix_pronouns(dict, speaker):
    dict = dict['pronoun']
    if 'person' in dict:
        if dict['person'] == 'first':
            return speaker
        elif dict['person'] == 'second':
            return 'leolani'

def dereference_pronouns_for_statement(words, rdf, speaker):

    first_word = rdf['subject'].split()[0]
    morphology = {}
    if first_word in grammar['pronouns']:
        morphology = grammar['pronouns'][first_word]

    if rdf['subject'].split()[0] in grammar['possessive']:
        morphology = grammar['possessive'][rdf['subject'].split()[0].lower()]
        if rdf['subject'].split()[1] in ['name', 'age', 'gender']:  # LIST OF PROPERTIES
            rdf['predicate'] = rdf['subject'].split()[1] + '-is'
            if len(words[3:]) > 1:
                for word in words[3:]:
                    rdf['object'] += ' ' + word
            else:
                rdf['object'] = words[3]


        elif rdf['subject'].split()[1] in ['favorite', 'best']:  # LIST OF POSSIBLE ADJECTIVES / PROPERTIES
            if rdf['subject'].split()[2] in grammar['categories']:  # LIST OF POSSIBLE CATEGORIES
                rdf['predicate'] = rdf['subject'].split()[1] + '-' + rdf['subject'].split()[2] + '-is'

    rdf['subject'] = fix_pronouns(morphology, speaker)

    if rdf['object'].split() and rdf['object'].split()[0] in grammar['pronouns']:
        morphology = grammar['pronouns'][rdf['object'].split()[0]]
        rdf['object'] = fix_pronouns(morphology, speaker)

        # TODO third person: pronoun coreferencing

    return rdf
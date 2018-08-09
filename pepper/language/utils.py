from __future__ import unicode_literals

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

from datetime import date
import random
import json
import re
import os

import logging


LOG = logging.getLogger(__name__)



wnl = WordNetLemmatizer()

ROOT = os.path.join(os.path.dirname(__file__))
json_dict = json.load(open(os.path.join(ROOT, 'dict.json')))
grammar = json_dict["grammar"]

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


def reply_to_question(brain_response):

    say = ''
    previous_author = ''
    previous_subject = ''
    previous_predicate = ''


    if len(brain_response['response'])==0: #FIX
        say = random.choice(["I don\'t know","i have no idea","i wouldn\'t know"])
        return say+'\n'

    for response in brain_response['response']:
        person = ''
        if 'authorlabel' in response and response['authorlabel']['value']!=previous_author:
            if response['authorlabel']['value'] == brain_response['question']['author']:
                say+=' you told me '
            else:
                say += response['authorlabel']['value'] +' told me '
            previous_author = response['authorlabel']['value']
        elif 'authorlabel' in response and response['authorlabel']['value']==previous_author:
            if brain_response['question']['predicate']['type'] != previous_predicate:
                say+=' that '

        if 'slabel' in response:
            if response['slabel']['value']==brain_response['question']['author']:
                say+= 'you'
                person = 'second'
            elif response['slabel']['value']=='Leolani':
                say+='I'
                person='first'

            elif (response['slabel']['value']==previous_subject) or (response['slabel']['value']==response['authorlabel']['value']):
                if response['slabel']['value'].lower() in ['bram','piek']:
                    say+= 'he'
                elif response['slabel']['value'].lower() in ['selene','lenka']:
                    say+= 'she'

            else:
                say += response['slabel']['value']
                previous_subject = response['slabel']['value']

        elif 'subject' in brain_response['question'] and brain_response['question']['subject']['label']!=previous_subject:
            if brain_response['question']['subject']['label'] == brain_response['question']['author']:
                person = 'second'
                say+=' you '
            elif brain_response['question']['subject']['label']=='Leolani':
                say+=' I '
                person = 'first'
            else:
                say += brain_response['question']['subject']['label']
            previous_subject = brain_response['question']['subject']['label']

        if brain_response['question']['predicate']['type'] in grammar['predicates']:
            if brain_response['question']['predicate']['type']==previous_predicate and 'slabel' in response and response['slabel']==previous_subject:
                pass
            else:
                previous_predicate = brain_response['question']['predicate']['type']
                if brain_response['question']['predicate']['type'] == 'is_from':
                    if person == 'first':
                        say += ' am from '
                    elif person == 'second':
                        say += ' are from'
                    else:
                        say += ' is from '
                else:
                    if person in ['first', 'second']:
                        say += ' ' + brain_response['question']['predicate']['type'][:-1] + ' '
                    else:
                        say += ' '+brain_response['question']['predicate']['type']+' '

        if 'olabel' in response:
            say += response['olabel']['value']
        elif 'object' in brain_response['question'].keys():
            if brain_response['question']['object']['label']==brain_response['question']['author']:
                say+='you'
            elif brain_response['question']['object']['label']=='Leolani':
                say+='me'
            else: say += brain_response['question']['object']['label']


        say+=' and '

    return say[:-5]

def write_template(speaker, rdf, chat_id, chat_turn, utterance_type):
    template = json.load(open(os.path.join(ROOT, 'template.json')))
    template['author'] = speaker.title()
    template['utterance_type'] = utterance_type
    if type(rdf) == str:
        return rdf
    template['subject']['label'] = rdf['subject'].strip().title() #capitalization
    template['predicate']['type'] = rdf['predicate'].strip()
    if rdf['object'] in names:
        template['object']['label'] = rdf['object'].strip().title()
        template['object']['type'] = 'PERSON'
    elif type(rdf['object']) is list:
        if rdf['object'][0].strip() == 'a':
            rdf['object'].remove(rdf['object'][0])
        template['object']['label'] = rdf['object'][0].strip().title()
        if len(rdf['object'])>1: template['object']['type'] = rdf['object'][1]
    else:
        if rdf['object'].lower().startswith('a '):
            rdf['object'] = rdf['object'][2:]
        template['object']['label'] = rdf['object'].strip().title()
    if template['object']['label'] in ['Soccer', 'Tacos', 'Baseball', 'Acrobatics', 'Cheese']: template['object']['label'] = template['object']['label'].lower()
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

def reply_to_statement(template, speaker):
    subject = template['statement']['subject']['label']
    predicate = template['statement']['predicate']['type']

    if predicate == 'isFrom': predicate = 'is from'

    object = template['statement']['object']['label']

    subject = 'you ' if speaker.lower()==subject.lower() else 'i' if subject.lower()=='leolani' else subject.title()
    if subject=='you ':
        predicate = fix_predicate_morphology(predicate)

    if subject =='i' and predicate.endswith('s'): predicate = predicate[:-1]

    if object.lower() == speaker.lower(): object='you'

    response = subject +' '+predicate+' '+object

    return response


def extract_roles_from_statement(words, speaker, viewed_objects):
    rdf = {'subject': '', 'predicate': '', 'object': ''}
    pos_list = pos_tag(words)
    i=0

    # OBJECT DETECTION SENTENCE
    if pos_list[0][0] in ['there', 'this', 'it']:
        if pos_list[1][0] in grammar['to be']:
            rdf['subject']=speaker
            rdf['predicate']='sees'
        for word in words[2:]:
            if word == 'no':
                rdf['predicate'] = 'sees-not'
            elif word!='a': # does it matter which objects leolani sees?
                rdf['object'] += (word + ' ')

    else:
        for pos in pos_list:
            if pos[1].startswith('V') or wnl.lemmatize(words[i]) in grammar['verbs']:
                if pos_list[i+1][0]=='from':
                    rdf['predicate'] = 'isFrom'
                    i+=1
                else:
                    rdf['predicate'] = words[i]+'s'if not words[i].endswith('s') else words[i]
                break
            rdf['subject']+=(words[i]+' ')
            i+= 1
        for word in words[i+1:]:
            rdf['object']+=(word+' ')
    return rdf


def check_rdf_completeness(rdf):
    for el in ['predicate', 'subject', 'object']:
        if not len(rdf[el]):
            LOG.warning("Cannot find {} in statement".format(el))
            return False
    if rdf['predicate'] not in grammar['predicates'] and not rdf['predicate'].endswith('-not'):
        LOG.error('Nonexisting predicate: {}'.format(rdf['predicate']))
        return False
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

    if 'pronoun' in np_info.keys() and 'person' in np_info['pronoun'].keys():
        rdf['subject'] = fix_pronouns(np_info['pronoun'], speaker)

    return rdf

def fix_pronouns(dict, speaker):
    if dict['person'] == 'first':
        return speaker
    elif dict['person'] == 'second':
        return 'leolani'

def dereference_pronouns_for_statement(words, rdf, speaker):

    first_word = rdf['subject'].split()[0]
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

    if rdf['object'].split()[0] in grammar['pronouns']:
        morphology = grammar['pronouns'][rdf['object'].split()[0]]
        rdf['object'] = fix_pronouns(morphology, speaker)

        # TODO third person: pronoun coreferencing

    return rdf
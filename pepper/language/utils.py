from __future__ import unicode_literals
from nltk.corpus import wordnet
import re
import json
import os
from datetime import date
import spacy
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
import random

from pepper.knowledge.theory_of_mind import TheoryOfMind
brain = TheoryOfMind(address = 'http://192.168.1.100:7200/repositories/leolani_test2')

wnl = WordNetLemmatizer()

from nltk.tag import StanfordNERTagger
ROOT = os.path.join(os.path.dirname(__file__))
ner = StanfordNERTagger(os.path.join(ROOT, 'stanford-ner', 'english.muc.7class.distsim.crf.ser'),
                        os.path.join(ROOT, 'stanford-ner', 'stanford-ner.jar'), encoding = 'utf-8')


properties = ['name', 'gender', 'movie']

'''
import wolframalpha
client = wolframalpha.Client('LA3GP6-VJ8KK8Y36A')

from nltk.stem.porter import *
stemmer = PorterStemmer()
'''


brain_response = [{
    "question": {
        "object": {
            "label": "",
            "type": "Country"
        },
        "predicate": {
            "type": "is_from"
        },
        "subject": {
            "label": "Bram",
            "type": "Person"
        }
    },
    "response": [
        {
            "authorlabel": {
                "type": "literal",
                "value": "Selene"
            },
            "olabel": {
                "type": "literal",
                "value": "Netherlands"
            }
        }
    ]
},
{
    "question": {
        "object": {
            "label": "Netherlands",
            "type": "Country"
        },
        "predicate": {
            "type": "is_from"
        },
        "subject": {
            "label": "Bram",
            "type": "Person"
        }
    },
    "response": [
        {
            "authorlabel": {
                "type": "literal",
                "value": "Selene"
            },
            "v": {
                "type": "uri",
                "value": "http://groundedannotationframework.org/grasp#CERTAIN"
            }
        }
    ]
},{
        "question": {
            "author": "jo",
            "chat": "",
            "date": "2018-03-19",
            "object": {
                "id": "",
                "label": "",
                "type": ""
            },
            "position": "",
            "predicate": {
                "type": "likes"
            },
            "response": {
                "format": "",
                "role": ""
            },
            "subject": {
                "id": "",
                "label": "piek",
                "type": ""
            },
            "turn": "",
            "utterance_type": "question"
        },
        "response": [
            {
                "authorlabel": {
                    "type": "literal",
                    "value": "selene"
                },
                "olabel": {
                    "type": "literal",
                    "value": "balkenbrij"
                }
            },
            {
                "authorlabel": {
                    "type": "literal",
                    "value": "bram"
                },
                "olabel": {
                    "type": "literal",
                    "value": "soccer"
                }
            },
            {
                "authorlabel": {
                    "type": "literal",
                    "value": "selene"
                },
                "olabel": {
                    "type": "literal",
                    "value": "horror movies"
                }
            },
            {
                "authorlabel": {
                    "type": "literal",
                    "value": "selene"
                },
                "olabel": {
                    "type": "literal",
                    "value": "2001 a space odyssey"
                }
            }
        ]
    }]

json_dict = json.load(open(os.path.join(ROOT, 'dict.json')))
grammar = json_dict["grammar"]

names = ['selene', 'bram', 'leolani', 'piek','selene']
statements = [['my favorite food is cake','lenka'],['I\'m from Amsterdam', 'Bram'],
              ['My name is lenka', 'person'],
              ['my mother is ljubica','lenka'],
               ['i like action movies', 'bram'],['bram likes romantic movies', 'selene'],
              ['bram is from Italy', 'selene']]  # [question, speaker]
questions = [['where is bram from?','jo'], ['what does piek like?', 'jo'], ['What is your name', 'person'],
             ['who is from italy?','jill'], ['Where is Selene from', 'person'], ['where are you from', 'person'], ['who do i know?', 'bram']]
             #['Have you ever met Michael Jordan?', 'piek'], ['Has Selene ever met piek', 'person'], ['Does Selene know piek', 'bram'],
             #['Does bram know Beyonce', 'person'], ['Do you know me','bram']]



def clean(word):
    clean_word = re.sub('[?!]','',word)
    return clean_word

def get_synonims(word):
    syns = wordnet.synsets(word)
    for s in syns:
        print(word+' - ' + s.lemmas()[0].name() + ': ' + s.definition())
        print(s.lemmas()[0].antonyms())




def reply(brain_response):
 # If i am talking to you ----- you told me piek likes / piek told me you like
    say = ''
    previous_author = ''
    previous_subject = ''
    person = ''

    if len(brain_response['response'])==0: #FIX
        say = random.choice(["I dont know","i have no idea","i wouldnt know"])
        return say+'\n'

    for response in brain_response['response']:
        if 'authorlabel' in response and response['authorlabel']['value']!=previous_author:
            say += response['authorlabel']['value'] +' told me '
            previous_author = response['authorlabel']['value']
        elif 'authorlabel' in response and response['authorlabel']['value']==previous_author:
            say+=' that '

        if 'slabel' in response:
            say += response['slabel']['value']
            previous_subject = brain_response['question']['subject']['label']
        elif 'subject' in brain_response['question']:
            if 'author' in brain_response['question'].keys() and brain_response['question']['subject']['label'] == brain_response['question']['author']:
                person = 'second'
                say+=' you '
            elif brain_response['question']['subject']['label']=='Leolani':
                say+=' I '
                person = 'first'
            else:
                say += brain_response['question']['subject']['label']
            previous_subject = brain_response['question']['subject']['label']

        if brain_response['question']['predicate']['type'] == 'is_from' and person!='first':
            say += ' is from '
        elif brain_response['question']['predicate']['type'] == 'is_from' and person=='first':
            say+= ' am from '
        elif brain_response['question']['predicate']['type'] in ['likes','knows'] and person!='second':
            say += ' '+brain_response['question']['predicate']['type']+' '
        else:
            say += ' ' + brain_response['question']['predicate']['type'][:-1] + ' '

        if 'olabel' in response:
            say += response['olabel']['value']
        elif 'object' in brain_response['question'].keys():
            say += brain_response['question']['object']['label']

        say+=' and '

    return say[:-5]+'\n'

def write_template(speaker, rdf, chat_id, chat_turn, utterance_type):
    template = json.load(open(os.path.join(ROOT, 'template.json')))
    template['author'] = speaker.title()
    template['utterance_type'] = utterance_type
    template['subject']['label'] = rdf['subject'].strip().title() #capitalization
    template['predicate']['type'] = rdf['predicate'].strip()
    if template['predicate']['type']=='is_from':
        template['predicate']['type'] = 'isFrom' #FIX
    if rdf['object'] in names:
        template['object']['label'] = rdf['object'].strip().title()
        template['object']['type'] = 'PERSON'
    elif len(rdf['object'])>1 and type(rdf['object']) is list:
        template['object']['label'] = rdf['object'][0].strip()
        template['object']['type'] = rdf['object'][1]
    else:
        template['object']['label'] = rdf['object'].strip()
    template['date'] = date.today()
    template['chat'] = chat_id
    template['turn'] = chat_turn
    return template


def say(template, person):
    subject = template['subject']['label']
    predicate = template['predicate']['type']
    object = template['object']['label']

    if person == 'third':
        predicate+='s'

    if person == 'second':
        subject = 'you'

    response = subject +' '+predicate+' '+object

    return response


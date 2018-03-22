from __future__ import unicode_literals
from nltk.corpus import wordnet
from nltk.stem.porter import *
from nltk import word_tokenize
from nltk.tag import StanfordNERTagger
import spacy
import wolframalpha
import re
import json
import os
from theory_of_mind import TheoryOfMind
brain = TheoryOfMind(address = 'http://192.168.1.103:7200/repositories/leolani_test2')
from datetime import date

# certain, uncertain, possible, probable
ROOT = os.path.join(os.path.dirname(__file__))
ner = StanfordNERTagger(os.path.join(ROOT, 'stanford-ner', 'english.muc.7class.distsim.crf.ser'),
                        os.path.join(ROOT, 'stanford-ner', 'stanford-ner.jar'), encoding='utf-8')

json_dict = json.load(open(os.path.join(ROOT, 'dict.json')))

client = wolframalpha.Client('LA3GP6-VJ8KK8Y36A')
stemmer = PorterStemmer()

grammar = json_dict["grammar"]
names = ['selene', 'bram', 'leolani', 'piek','selene']
statements = [['where is bram from?','jo'],['my favorite food is cake','lenka'],['what does piek like?', 'jo'],['I\'m from the Netherlands', 'Bram'],
              ['What is your name', 'person'],['My name is lenka', 'person'],
              ['my mother is ljubica','lenka'], ['Does Selena know piek', 'bram'],['who is from italy?','jill'],
            ['Where is Selene from', 'person'], ['where are you from', 'person'], 
             ['Have you ever met Michael Jordan?', 'piek'], ['Has Selene ever met piek', 'person'],
             ['Does bram know Beyonce', 'person'], ['Do you know me','bram'],['Do you know him','bram'],
               ['i like action movies', 'bram'],['bram likes romantic movies', 'selene'],
              ['bram is from Italy', 'selene']]  # [question, speaker]


def clean(word):
    clean_word = re.sub('[?!]','',word)
    return clean_word

def get_synonims(word):
    syns = wordnet.synsets(word)
    for s in syns:
        print(word+' - ' + s.lemmas()[0].name() + ': ' + s.definition())
        print(s.lemmas()[0].antonyms())

def analyze_question(speaker, words, pos_list):
    ambig = 0
    morphology = {}
    to_be = ''
    main_verb = ''
    say = ''
    response_type = ''

    rdf = {'subject':'','predicate':'','object':''}

    question_word = words[0].lower().strip()

    # SETTING THE RESPONSE TYPE
    if question_word in grammar["question words"]:
        response_type = grammar["question words"][question_word]["response"]
    elif pos_list[0][1].startswith('VB'):
        to_be = question_word
        response_type = 'bool'

    '''
    if pos_list[0][0].lower() == 'have' or words[2].lower().strip() == 'ever':
        response_type += '-frequency'
    '''
   # print('because the question word is '+question_word+', response type is '+response['type'])

    # EXTRACTING THE MAIN VERB AND TO BE
    for pos in pos_list[1:]:
        if pos[0] not in names:
            if pos[0].lower() in grammar['to be'] and to_be=='':
                to_be=pos[0]
                morphology["tense"] = grammar['to be'][to_be]['tense']
                if 'person' in grammar['to be'][to_be]:
                    morphology['person'] = grammar['to be'][to_be]['person']
            elif pos[1].startswith('VB'):
                main_verb = pos[0]
            elif 'like' in words:
                main_verb='like'
    print('be: ' + to_be + ', verb:' + main_verb)
    if main_verb.endswith('ing'):
        morphology['duration'] = 'continuous'
    if main_verb.endswith('d'):
        morphology['duration'] = 'done'


    # FINDING THE SUBJECT OF THE SENTENCE
    # TODO DEALING WITH LASTNAMES
    subject = list()
    if question_word == 'have':
        subject.append(words[1])
    else:
        subject.append(words[words.index(to_be) + 1])
    if subject[0].lower() == 'selena':
        subject[0] = 'selene'

    if subject[0] in grammar['pronouns']:
        morphology['pronoun_info'] = grammar['pronouns'][subject[0]]
        if subject[0] == 'i':
            subject.append(speaker)
        elif subject[0] == 'you':
            subject.append('leolani')
        else: #PRONOUN COREFERENCE RESOLUTION
            say+='I am not sure which '+subject[0]+' you think '
            ambig = 1

    print('subject '+str(subject))
    rdf['subject'] = subject[len(subject)-1]
    if to_be != '' and main_verb == '':
        main_verb = to_be
    else:
        rdf['predicate'] = main_verb+'s'

     #  print('subject: ' + str(subject))

    #FINDING THE OBJECT OF THE SENTENCE
    obj = words[words.index(main_verb) + 1:]
    if obj:
      #  print('obj: ' + str(obj))
        if obj[0] == 'your':
            obj = words[3].lower().strip()
            subject = 'my ' + obj

            say = subject+' is '+' ...hmmm'
            print(say)
    #        if obj in people[len(people)-1].keys():
                # WHAT IS YOUR X
    #            say += subject+' '+to_be+ ' '+ people[len(people)-1][obj]

    if len(obj)>0 and obj[0] in grammar['pronouns']:
        pr = obj[0]
        morphology['obj pronoun'] = grammar['pronouns'][pr]
        if pr in ['me','I']:
            obj[0] = speaker
        elif pr=='you':
            obj[0] = 'leolani'
        else:
            say = ' which '+obj[0]+' you mean?'
            ambig = 1

    # WHERE IS X FROM / WHERE ARE YOU FROM / WHO IS FROM X
    if 'from' in words:
        rdf['predicate'] = 'isFrom'
        '''
        if question_word=='where':
            rdf['object'] = 'LOCATION'
        if question_word=='who':
            rdf['subject'] = 'PERSON'
        '''
        if len(words) > words.index('from')+1 and question_word=='who':
            rdf['object'] = words[words.index('from')+1]
        for name in names:
            if name in subject:
                subject = name
                rdf['subject'] = subject
                #if names.count(person['name'])>1 and 'lastname' in person.keys():
                #    subject+=' '+person['lastname']+' '
                #if name == 'leolani':
                #    subject = ' I '
                #    to_be = 'am'
                #if 'from' in person.keys():
                #    say += ' '+subject+' '+to_be + " " + 'from' + ' ' + person['from']
                #else:
                #    say += "I don't know"+question_word+' '+person['name']+' '+to_be+ ' from'


    # DOES X KNOW Y / HAS X MET Y / DO YOU KNOW Y
    if (stemmer.stem(main_verb) =='know' or main_verb=='met') and ambig == 0:
        rdf['predicate'] = 'knows'
        rdf['object'] = obj[0]
        rdf['subject'] = 'PERSON'
        for s in subject:
            if s in names:
                rdf['subject'] = s
                #if s =='leolani':
                #    if obj[0] in people[len(people)-1]['knows']:
                #        to_be = ''
                #    else:
                #        if to_be == 'have':
                #            to_be += ' not'
                #        else:
                #            main_verb += ' not '
                #    if obj[0]==speaker:
                #        obj[0] = 'you, '+speaker
                #    say += 'I '+to_be+' '+main_verb+' '+obj[0]
                #else:
                #    for person in people:
                #        if person['name']==s:
                #            if speaker == 'person':
                #                speaker = ''
                #            else:
                #                speaker+=' '
                #            if 'knows' in person.keys() and obj[0] in person['knows']:
                #                say += 'yes, '+speaker+s+' knows '+obj[0]
                 #           else:
                 #               say += ' no, '+speaker+s+ ' '+to_be +' not '+main_verb+' '+obj[0]

    '''
    if names.count(subject[0])>1 or names.count(obj[0])>1:
        print('I know two people with that name')
        ambig = 1
    '''
        #for word in say.split(' '):
        #    if names.count(word)>1:
        #        for person in people:
        #            if person['name']==word and 'lastname' in person.keys():
        #                print(word+' '+person['lastname'])
        #        break

   # print('response info: ' + str(response))
   # print('extracted morphological info: ' + str(morphology))
    if say:
        print('response:'+say)
    else:
        print(str(subject) + " " + to_be + " " + main_verb + "..." + response_type + ' ' + str(obj))
        print('i got confused')

    template = json.load(open(os.path.join(ROOT, 'template.json')))
    template['author'] = speaker
    template['utterance_type'] = 'question'
    template['subject']['label'] = rdf['subject'].strip()
    template['predicate']['type'] = rdf['predicate'].strip()
    if rdf['object'] in names:
        template['object']['label'] = rdf['object'].strip()
        template['object']['type'] = 'PERSON'
    else:
        template['object']['label'] = rdf['object'].strip()
    template['date'] = date.today()
    # return [rdf, speaker, 'question']

    print(template)

    return template




def analyze_statement(speaker, words, pos_list):

    rdf = {'subject': '', 'predicate': '', 'object': ''}

    morphology = dict()
    to_be=''
    main_verb=''
    subject=[]
    say = ''

    # FINDING THE MAIN VERB AND TO_BE
    for pos in pos_list[1:]:
        if pos[0] not in names:
            if pos[0].lower() in [grammar['to be'],'\'m','\'s'] and to_be=='':
                to_be=pos[0]
                if to_be in grammar['to be']:
                    morphology["tense"] = grammar['to be'][to_be]['tense']
                    if 'person' in grammar['to be'][to_be]:
                        morphology['person'] = grammar['to be'][to_be]['person']
            elif (pos[1].startswith('VB') or pos[0] in grammar['verbs']) and main_verb=='':
                main_verb = pos[0]
    print('be: ' + to_be + ', verb:' + main_verb)
    if main_verb.endswith('ing'):
        morphology['duration'] = 'continuous'
    if main_verb.endswith('d'):
        morphology['duration'] = 'done'
    #print(morphology)

    # FINDING THE SUBJECT
    if pos_list[0][1].startswith('PRP') or pos_list[0][0].lower() in names:
        #if main_verb in ['know','think']:
        if to_be not in ['','\'m', '\'s']: # FIX: I'M, YOU'RE, ....
            subject.append(words[words.index(to_be)-1])
        else:
            subject.append(pos_list[0][0])
        if pos_list[0][0].lower() in grammar['pronouns']:
            morphology['pronoun_info']=grammar['pronouns'][pos_list[0][0].lower()]
            if morphology['pronoun_info']['person'] == 'first':# and main_verb not in ['think','assume','believe']:
                subject.append(speaker)
                #print('subject is '+speaker)
            if morphology['pronoun_info']['person'] == 'second':
                subject.append('leolani')

        if subject[0].lower() == 'my':
            subject.pop()
            subject.append(speaker)

            print(subject)

            '''
            if subject[0] in names:
                subject.append(subject[0]+'\'s '+ pos_list[1][0])
            else:
                subject.append('your '+pos_list[1][0])
            '''

            #subject.pop(0)
        #else:
        #    subject.append(pos_list[0][0]+' '+pos_list[1][0])

    if len(subject) == 0:
        rdf['subject'] = ''
    else:
        #print('subject is '+subject[len(subject)-1])
        rdf['subject'] = subject[len(subject)-1]

    obj = ''
    if main_verb in words:
        for word in words[words.index(main_verb) + 1:]:
            obj+= ' ' + word
    elif main_verb=='\'m':
        for word in words[1:]:
            obj += ' ' + word
        if morphology['pronoun_info']['person']=='first':
            main_verb = 'is'
    elif 'from' in words:
        for word in words[words.index('from') + 1:]: #FIX
            obj+= ' ' + word

    if obj:
        rdf['predicate'] = main_verb
        #  print('obj: ' + str(obj))
        if obj[0] == 'your':
            obj = words[3].lower().strip()
        rdf['object'] = ''
        for o in obj.split():
            if o != 'from':
                rdf['object'] = rdf['object'] + ' ' + o

    if len(pos_list)>2 and pos_list[2][0]=='from':
        rdf['predicate'] = 'isFrom'

        '''
        if subject[len(subject)-1] in names:
            for person in people:
                if person['name'] == subject[len(subject)-1]:
                    if 'from' in person.keys():
                        print("i thought "+person['name'] +' is from '+person['from'])
        '''

    # knows person, studies at, works at, lives_in, visited, likes, dislikes
    # working with plural

    for sub in subject:
        if (sub in names) or (sub == 'person'):
            rdf['subject'] = sub

    print(rdf['subject'],speaker)

    '''
    if rdf['subject'].lower()!=speaker.lower() and speaker!='person':
        morphology['pronoun_info']['person'] = 'third'
    '''

    '''
    if stemmer.stem(main_verb) =='like':
        if subject[len(subject) - 1] in names:
            for person in people:
                if person['name'] == subject[len(subject) - 1]:
                    if 'likes' in person.keys():
                        print('looking up '+person['name'])
                        if subject[0]=='i':
                            say+='i have heard you like '+person['likes']+' '

                        else:
                            say+="i have heard " + person['name'] + ' likes ' + person['likes']+' '
    '''

    if main_verb in ['know', 'like', 'live']:
        rdf['predicate']+='s'
        if morphology['pronoun_info']['person'] == 'third':
            main_verb = main_verb + 's'

    if main_verb == 'is' and words[0].lower()=='my':
        print(words[1].lower())
        if words[1].lower() == 'favorite':
            rdf['predicate'] = 'favorite '+words[2].lower()+'-is'
            print(rdf['predicate'])
        else:
            rdf['predicate'] = words[1].lower() + '-is'

    '''
    if len(subject)>0:
        say+=subject[len(subject)-1]+' '+main_verb + ' '+str(obj)
    else:
        say+='i got confused' #unknown sentence
    print(say)
    '''

    template = json.load(open(os.path.join(ROOT, 'template.json')))
    template['author'] = speaker
    template['utterance_type']='statement'
    template['subject']['label']=rdf['subject'].strip()
    template['predicate']['type'] = rdf['predicate']
    if rdf['object'] in names:
        template['object']['label'] = rdf['object'].strip()
        template['object']['type'] = 'PERSON'
    else:
        template['object']['label'] = rdf['object'].strip()
    #return [rdf, speaker, 'statement']
    template['date'] = date.today()
    print(template)
    brain.update(template)


    if rdf['subject'].lower() == speaker.lower():
        speaker = 'you'
        rdf['subject'] = 'you'

    if 'from' in words:
        if speaker=='you':
            main_verb = ' are from '
        else:
            main_verb = 'is from'

    if '-' in rdf['predicate']:
        prop = rdf['predicate'].split('-')[0]
        print(prop)
        if rdf['subject'] == 'you':
            rdf['subject'] = 'your '+prop

    say = speaker + ' said ' + rdf['subject'] + ' ' + main_verb + ' ' + rdf['object']

    return say

# for st in statements:
def analyze_utterance(utterance, speaker):
    print('--------------------------------------------------------')
    print('utterance: '+utterance+', speaker: '+speaker)
    words_raw = utterance.lower().split(" ")
    words = []
    for word in words_raw:
        words.append(clean(word))

    nlp = spacy.load('en')
    doc = nlp(utterance)
    pos_list = []

    recognized_entities = []

    tok = word_tokenize(utterance)

    ner_text = ner.tag(tok)
    for n in ner_text:
        if n[1]!='O':
            recognized_entities.append(n)

    # instead of 'Michael', 'Jordan' => 'Michael Jordan'
    i = 0
    for el in recognized_entities:
        if len(recognized_entities) > i+1 and el[1]==recognized_entities[i+1][1]:
            recognized_entities.append([el[0] + ' '+recognized_entities[i+1][0],el[1]])
            recognized_entities.remove(recognized_entities[i+1])
            recognized_entities.remove(el)
        i+=1
    #print(recognized_entities)

    for token in doc:
        pos_list.append([token.text, token.tag_])
    print(pos_list)

    if pos_list[0][1] in ['WP', 'WRB','VBZ','VBP']:
        template = analyze_question(speaker, words, pos_list)
        print('i am thinking')
        response = (reply(brain.query_brain(template)))
    else:
        response= analyze_statement(speaker, words, pos_list)
        #print(brain.update(template))

    return response



def reply(brain_response):

    say = ''
    previous_author = ''
    previous_subject = ''

    if len(brain_response['response'])==0:
        say = "I dont know if "
        say += brain_response['question']['subject']['label'] + ' '
        say += brain_response['question']['predicate']['type'] + ' '
        say += brain_response['question']['object']['label']
        return say+'\n'

    print(brain_response)

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
            say += brain_response['question']['subject']['label']
            previous_subject = brain_response['question']['subject']['label']

        if brain_response['question']['predicate']['type'] == 'isFrom':
            say += ' is from '
        elif brain_response['question']['predicate']['type'] == 'likes':
            say += ' likes '

        if 'olabel' in response:
            say += response['olabel']['value']
        elif 'object' in brain_response['question'].keys():
            say += brain_response['question']['object']['label']

        say+=' and '

    return say[:-5]+'\n'


brain_response = [{
    "question": {
        "object": {
            "label": "",
            "type": "Country"
        },
        "predicate": {
            "type": "isFrom"
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
            "label": "Piek",
            "type": "Person"
        },
        "predicate": {
            "type": "knows"
        },
        "subject": {
            "label": "Selene",
            "type": "Person"
        }
    },
    "response": []
},
{
    "question": {
        "object": {
            "label": "Netherlands",
            "type": "Country"
        },
        "predicate": {
            "type": "isFrom"
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

#print(analyze_utterance('what does selene like?','jo'))
#u'predicate': {u'type': u'PREDICATE'}, u'chat': u'', u'author': u'jo', u'object': {u'type': u'', u'id': u'', u'label': u'OBJECT'}, u'turn': u'', u'utterance_type': u'question', u'date': datetime.date(2018, 3, 18), u'position': u'',
#  u'response': {u'role': u'', u'format': u''}, u'subject': {u'type': u'', u'id': u'SUBJECT', u'label': u''}}


for resp in brain_response:
    print(reply(resp))

#for stat in statements:
#    rdf = analyze_utterance(stat[0],stat[1])










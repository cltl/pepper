from nltk import pos_tag
from analyzers import *
from theory_of_mind import TheoryOfMind
#from pepper.knowledge.theory_of_mind import TheoryOfMind

test_mode = 1 # FOR ADDITIONAL PRINTS

def analyze_question(speaker, words, chat_id, chat_turn):
    rdf = {'subject':'','predicate':'','object':''}

    tagged = pos_tag(words)
    first_word = words[0].lower().strip()

    # SETTING THE QUESTION TYPE
    # 1a: WH VERB SUBJECT VERB [WHERE DO YOU LIVE? WHO LIVES WITH YOU?]
    # 1b: WH VERB POS OBJECT [WHAT IS YOUR FAVORITE BOOK?]
    # 2: TO_BE SUBJECT VERB OBJECT [DO YOU LIKE EGGS?]

    if first_word in grammar['question words']:
        response_type = grammar['question words'][first_word]
        category='wh_question'
    elif first_word in grammar['to be'] or first_word in ['have','has','can']:
        response_type = 'bool'
        category='verb_question'
    else:
        response_type = 'unspecified'

    print(response_type)

    if category == 'wh_question':

        verb = words[1].lower().strip()
        verb_info = analyze_verb(verb)

        third_word = words[2].lower().strip()
        third_pos = pos_tag([third_word])[0][1]

        if third_pos in ['PRP$','NN','PRP']: # what is YOUR favorite movie, where are YOU from, who likes PUPPIES, what do YOU like
            nn = [third_word]
            i=3

            for pos in tagged[3:]:
                if pos[1]=='IN': # where are you FROM

                    if words[i]=='from':
                        rdf['predicate'] = 'is_from'
                    elif words[i]=='like': # what do you LIKE
                        if verb in ['do', 'does']:
                            verb_info = analyze_verb(words[i])

                        elif verb in ['is','are']: # what is your life LIKE
                            print('similarity question')


                        if 'predicate' in verb_info.keys():
                            rdf['predicate'] = verb_info['predicate']

                        print('verb', verb_info, type(verb_info))
                    break
                elif not pos[1].startswith('V'):
                    nn.append(words[i])
                    i+=1

            nn_info = analyze_nn(nn, speaker)
            print('nn ',nn_info,type(nn_info))
            if 'object' in nn_info.keys():
                rdf['object'] = nn_info['object']
            if 'subject' in nn_info.keys():
                rdf['subject'] = nn_info['subject']
            if 'predicate' in nn_info.keys():
                rdf['predicate'] = nn_info['predicate']

            if 'human' in nn_info.keys():
                rdf['subject']=nn_info['human']

            if 'pronoun' in nn_info.keys() and 'person' in nn_info['pronoun'].keys():
                if nn_info['pronoun']['person']=='first':
                    rdf['subject'] = speaker
                elif nn_info['pronoun']['person']=='second':
                    rdf['subject'] = 'leolani'

            print('rdf', rdf)

            if words[3].lower().strip() in ['know','like']:
                verb_info = analyze_verb(words[3].lower().strip())
                if 'predicate' in verb_info.keys():
                    rdf['predicate']=verb_info['predicate']

            print('verb ',verb_info, type(verb_info))

        if third_pos == 'IN':
            if third_word == 'from':
                rdf['predicate'] = 'is_from'
                for word in words[3:]:
                    rdf['object'] += (word + ' ')



    elif category=='verb_question': # DO you like puppies, CAN you ski
        i=1
        nn = words[1]

        print('nn',nn)

        for pos in tagged[2:]:
            if (not pos[1].startswith('V') and words[i+1] not in ['ever']) or pos[0] in names:
                nn += words[i].lower().strip()
                i+=1
            else:
                break

        nn_info = analyze_nn(nn, speaker)
        if 'pronoun' in nn_info and 'person' in nn_info['pronoun']:
            if nn_info['pronoun']['person']=='second':
                rdf['subject']='leolani'

        verb = words[i+1]
        verb_info = analyze_verb(verb)
        if 'predicate' in verb_info:
            rdf['predicate'] = verb_info['predicate'] # 'knows' instead of 'know' - predicate mapping

        remain = []
        while len(words)>i+2:
            remain.append(words[i+2])
            i+=1

        for word in remain:
            if pos_tag([word])[0][1].startswith('V') or word=='met':
                verb_info = analyze_verb(remain[0])
                print('verb ', verb_info)
            else:
                nn_info = analyze_nn([word], speaker)
                if 'pronoun' in nn_info and 'person' in nn_info['pronoun']:
                    if nn_info['pronoun']['person'] == 'first':
                        rdf['object'] = speaker
                    elif nn_info['pronoun']['person'] == 'second':
                        rdf['subject'] = 'leolani'
                elif 'entities' in nn_info:
                    print(nn_info['entities'])





                                # OBJECT - 4TH WORD

    template = write_template(speaker, rdf,chat_id, chat_turn, 'question')
    return template

def analyze_statement(speaker, words, chat_id, chat_turn):

    print(words)

    morphology = {'person':''}
    rdf = {'subject': '', 'predicate': '', 'object': ''}
    pos_list = pos_tag(words)
    i=0
    for pos in pos_list:
        print(pos[0],pos[1])
        if pos[1].startswith('V') or wnl.lemmatize(words[i]) in grammar['verbs']:
            rdf['predicate'] = words[i]
            print(rdf['predicate'])
            break
        rdf['subject']+=(words[i]+' ')
        i+= 1
    for word in words[i+1:]:
        rdf['object']+=(word+' ')

    if rdf['subject'].split()[0].split('\'')[0].lower() in grammar['pronouns']:
        morphology = grammar['pronouns'][rdf['subject'].split()[0].split('\'')[0].lower()]
        if '\'' in rdf['subject'] and rdf['subject'].split()[0].split('\'')[1].lower() in ['m','re']:
            rdf['predicate'] = rdf['subject'].split()[1:]

            if rdf['predicate'][0]=='from':
                for word in rdf['predicate'][1:]:
                    if word!='the':
                        rdf['object'] += ' '+word

                info = analyze_nn([rdf['object']], speaker)

                if 'entities' in info:
                    print(info['entities'][0][1])
                    entity = info['entities'][0][1].encode('ascii','ignore')

                    rdf['object'] = [rdf['object'],entity]

                rdf['predicate'] = 'is_from'



    if rdf['subject'].strip() in grammar['pronouns']:
        morphology = grammar['pronouns'][rdf['subject'].strip()]

    if morphology['person'] == 'first':
        rdf['subject'] = speaker
    elif morphology['person'] == 'second':
        rdf['subject'] = 'leolani'
        # TODO third person: pronoun coreferencing

    if rdf['subject'].split()[0].lower() in grammar['possessive']:
        morphology = grammar['possessive'][rdf['subject'].split()[0].lower()]

        #print(morphology)

        if rdf['subject'].split()[1] in ['name','age','gender']: #LIST OF PROPERTIES
           rdf['predicate'] = rdf['subject'].split()[1]+'-is'

           if len(words[3:])>1:
               for word in words[3:]:
                   rdf['object']+= ' '+word

           else:
               rdf['object'] = words[3]

           #print(rdf)


        elif rdf['subject'].split()[1] in ['favorite','best']: # LIST OF POSSIBLE ADJECTIVES / PROPERTIES
            if rdf['subject'].split()[2] in ['book','movie','friend','food']: # LIST OF POSSIBLE CATEGORIES
                rdf['predicate']= rdf['subject'].split()[1]+'-'+rdf['subject'].split()[2]+'-is'
                print(rdf['predicate'])
                print(rdf['object'])

        if morphology['person'] == 'first':
            rdf['subject'] = speaker



    #IF PERSON


    template = write_template(speaker, rdf, chat_id, chat_turn,'statement')



    return template

    '''
    
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

            
            if subject[0] in names:
                subject.append(subject[0]+'\'s '+ pos_list[1][0])
            else:
                subject.append('your '+pos_list[1][0])
            

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
        rdf['predicate'] = 'is_from'

    # knows person, studies at, works at, lives_in, visited, likes, dislikes
    # working with plural

    for sub in subject:
        if (sub in names) or (sub == 'person'):
            rdf['subject'] = sub

    print(rdf['subject'],speaker)

    
    if rdf['subject'].lower()!=speaker.lower() and speaker!='person':
        morphology['pronoun_info']['person'] = 'third'
    

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
    template['chat'] = chat_id
    template['turn'] = chat_turn
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

    if len(say.split()) < 3:
        say = random.choice(['Can you repeat your statement?','I am not sure what you said','Sorry, I didnt quite hear you...'])

    return say
    '''

def process_utterance(utterance, speaker, chat_id, chat_turn):
    print('--------------------------------------------------------')
    print('utterance: '+utterance+', speaker: '+speaker)
    words_raw = utterance.split()
    words = []
    for word in words_raw:
        words.append(clean(word))

    if pos_tag([words[0]])[0][1] in ['VB','WP', 'WRB','VBZ','VBP'] or words[0].lower() in grammar['to be']:
        template = analyze_question(speaker, words, chat_id, chat_turn)
        #response = (reply(brain.query_brain(template)))
    else:
        template = analyze_statement(speaker, words, chat_id, chat_turn)
        #print(brain.update(template))

    return template



def run_tests():

    brain = TheoryOfMind()
    print(brain.get_predicates())
    chat_turn = 0
    chat_id = 0

    '''
    for stat in statements:
        rdf = process_utterance(stat[0], stat[1], chat_id, chat_turn)
        print(rdf)
        response = brain.update(rdf)
        print(response)
        chat_turn += 1
    '''

    for ques in questions:
        template = process_utterance(ques[0], ques[1], chat_id, chat_turn)
        print(template)
        response = brain.query_brain(template)
        print(response)
        print(reply(response))
        chat_turn += 1


run_tests()

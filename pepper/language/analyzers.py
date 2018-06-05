from utils import *

def analyze_question_word(question_word, pos):
    if question_word in grammar["question words"]:
        response_type = grammar["question words"][question_word]["response"]
    elif pos.startswith('VB'):
        to_be = question_word
        response_type = 'bool'
        # print('because the question word is '+question_word+', response type is '+response['type'])
    return response_type

def analyze_nn(nn_list, speaker):

    morphology = {}
    # object containing some property from brain? containing 'favorite'?

    if type(nn_list) is list:
        first_word = nn_list[0]
    else:
        first_word = nn_list

    #print(first_word)

    if first_word in grammar['pronouns']:

        morphology['pronoun'] = analyze_pronoun(first_word, speaker)

    elif first_word in names:
        morphology['human'] =  first_word

    elif first_word in grammar['possessive']:
        morphology = grammar['possessive'][first_word]

        for word in nn_list[1:]:
            #print(word, pos_tag([word]))
            if word in properties: # your mother's maiden name?
                morphology['object'] = word
                if morphology['person'] == 'second':
                    morphology['subject'] = 'leolani'
                if morphology['person'] == 'first':
                    morphology['subject'] = 'speaker'

        morphology['predicate']=nn_list[1]+'-is'

        #print('analyzer',morphology)


    else:
        recognized_entities = []

        ner_text = ner.tag(nn_list)
        print('NER',ner_text)

        for n in ner_text:
            if n[1] != 'O':
                recognized_entities.append(n)

        # instead of 'Michael', 'Jordan' => 'Michael Jordan'
        i = 0
        for el in recognized_entities:
            if len(recognized_entities) > i + 1 and el[1] == recognized_entities[i + 1][1]:
                recognized_entities.append([el[0] + ' ' + recognized_entities[i + 1][0], el[1]])
                recognized_entities.remove(recognized_entities[i + 1])
                recognized_entities.remove(el)
            i += 1
            # print(recognized_entities)
        morphology['entities'] = recognized_entities

    return morphology

def analyze_pronoun(pronoun, speaker):
    morphology = {}

    if pronoun in grammar['possessive']:
        morphology = grammar['possessive'][pronoun]

    elif pronoun in grammar['pronouns']:
        morphology = grammar['pronouns'][pronoun]

    #if speaker!='leolani' and morphology['person']=='second':
    #    morphology['']

    return morphology


def analyze_to_be(to_be):
    morphology = grammar['to be'][to_be]
    return morphology


def analyze_verb(verb):

    morphology = {}

    if verb in grammar['to be']:
        morphology['to be'] = analyze_to_be(verb)

    else:
        verb_lemma = wnl.lemmatize(verb, pos='v')
        if verb_lemma in ['know', 'live', 'like', 'have']:
           morphology['predicate'] = verb_lemma+'s'
        if verb.endswith('s'):
            morphology['person']='third'

    return morphology


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

    first_word = (nn_list[0] if (type(nn_list) is list) else nn_list)

    if first_word in grammar['pronouns']:
        morphology['pronoun'] = analyze_pronoun(first_word, speaker)

    elif first_word in names:
        morphology['human'] =  first_word
        # what if it is a name but not of an acquaintance?

    elif first_word in grammar['possessive']:
        morphology = analyze_possessive_nn(first_word, nn_list)

    #else:
    #    morphology['entities'] = extract_named_entities(nn_list)

    return morphology

def analyze_possessive_nn(poss, nn_list):
    morphology = grammar['possessive'][poss]

    for word in nn_list[1:]:
        # print(word, pos_tag([word]))
        if word in grammar['categories']:  # your friends's  name?
            morphology['object'] = word
            if morphology['person'] == 'second':
                morphology['subject'] = 'leolani'
            if morphology['person'] == 'first':
                morphology['subject'] = 'speaker'

    morphology['predicate'] = nn_list[1] + '-is'

    return morphology

def extract_named_entities(nn_list):

    from nltk.tag import StanfordNERTagger
    ROOT = os.path.join(os.path.dirname(__file__))
    ner = StanfordNERTagger(os.path.join(ROOT, 'stanford-ner', 'english.muc.7class.distsim.crf.ser'),
                            os.path.join(ROOT, 'stanford-ner', 'stanford-ner.jar'), encoding='utf-8')

    recognized_entities = []

    ner_text = ner.tag(nn_list)
    print('NER', ner_text)

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
    return recognized_entities

def analyze_pronoun(pronoun, speaker):
    morphology = {}

    if pronoun in grammar['possessive']:
        morphology = grammar['possessive'][pronoun]

    elif pronoun in grammar['pronouns']:
        morphology = grammar['pronouns'][pronoun]

    #if speaker!='leolani' and morphology['person']=='second':
    #    morphology['']

    return morphology



def analyze_verb(verb):

    morphology = {}

    if verb in grammar['to be']:
        morphology['to be'] = grammar['to be'][verb]

    else:
        verb_lemma = wnl.lemmatize(verb, pos='v')
        if verb_lemma in grammar['verbs']:
           morphology['predicate'] = verb_lemma+'s'
        if verb.endswith('s'):
            morphology['person']='third'

    return morphology


def analyze_wh_question(words, speaker, response_type):
    tagged = pos_tag(words)
    rdf = {'subject': '', 'predicate': '', 'object': ''}


    if words[1].strip() in grammar['to be']:
        to_be = words[1].strip()
        morphology = grammar['to be'][to_be]
    elif words[1].strip() in grammar['verbs'].keys()+grammar['predicates']:
        rdf['predicate'] = words[1].strip()
        rdf['object'] = words[2]

    else:
        return "I seem to have misunderstood the word "+to_be+" in your question"

    third_word = words[2].lower().strip()
    third_pos = pos_tag([third_word])[0][1]

    if third_pos in ['PRP$', 'NN','PRP']:
        nn = [third_word]

        for pos in tagged[3:]:
            if pos[1] == 'IN':  # where are you FROM
                if pos[0] == 'from': rdf['predicate'] = 'is_from'
                break
            elif not pos[1].startswith('V'):
                nn.append(pos[0])

        nn_info = analyze_nn(nn, speaker)
        rdf = pack_rdf_from_nn_info(nn_info, speaker, rdf)

        if len(words)>3 and wnl.lemmatize(words[3].lower().strip(), 'v') in grammar['verbs']:
            verb_info = analyze_verb(words[3].lower().strip())
            if 'predicate' in verb_info.keys():
                rdf['predicate'] = verb_info['predicate']

    elif third_pos == 'IN':
        if third_word == 'from':
            rdf['predicate'] = 'is_from'
            for word in words[3:]:
                rdf['object'] += (word + ' ')

    else:
        return "This word "+third_word+" is surprising me..."

    print('analysis of wh-question produced this rdf: ', rdf)
    return rdf


def analyze_verb_question(words, speaker):
    tagged = pos_tag(words)
    rdf = {'subject': '', 'predicate': '', 'object': ''}

    # extract subject
    nn, index = extract_nn(words, tagged, index=1)
    nn_info = analyze_nn(nn, speaker)

    #if 'pronoun' in nn_info and 'person' in nn_info['pronoun']:
    #    if nn_info['pronoun']['person'] == 'second':
    #        rdf['subject'] = 'leolani'

    verb = words[index + 1]
    verb_info = analyze_verb(verb)

    if 'predicate' in verb_info:
        rdf['predicate'] = verb_info['predicate']  # 'knows' instead of 'know' - predicate mapping

    '''
    remain = []
    while len(words) > index + 2:
        remain.append(words[index + 2])
        index += 1
    '''

    for word in words[index+2:]:
        if pos_tag([word])[0][1].startswith('V') or word == 'met':
            verb_info = analyze_verb(word)
            print('verb ', verb_info)
        else:
            nn_info = analyze_nn([word], speaker)
            if 'pronoun' in nn_info and 'person' in nn_info['pronoun']:
                if nn_info['pronoun']['person'] == 'first':
                    rdf['object'] = speaker
                elif nn_info['pronoun']['person'] == 'second':
                    rdf['subject'] = 'leolani'
            #elif 'entities' in nn_info:
            #    print(nn_info['entities'])

    return rdf


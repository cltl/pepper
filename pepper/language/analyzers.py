from utils import *
import logging


LOG = logging.getLogger(__name__)


def analyze_question_word(question_word, pos):
    '''
    This function returns the response type of a question based on its first word
    '''

    if question_word in grammar["question words"]:
        response_type = grammar["question words"][question_word]["response"]

    elif pos.startswith('VB'):
        response_type = 'bool'

    else:
        LOG.error('unknown question word: '+question_word)

    return response_type


def analyze_np(np_list, speaker):
    '''
    This function analyzes a noun phrase (consists of pronouns, nouns, names, or possessive pronouns + prepositions)
    Morphological information which is stored in pronouns is extracted, names are simply marked as 'human' and
    possessive syntax constructions are analyzed
    '''
    morphology = {}

    first_word = (np_list[0] if (type(np_list) is list) else np_list)

    if first_word in grammar['pronouns']:
        morphology['pronoun'] = analyze_pronoun(first_word, speaker)

    elif first_word in names:
        morphology['human'] = first_word
        # what if it is a name but not of an acquaintance?

    elif first_word in grammar['possessive']:
        morphology = analyze_possessive_np(first_word, np_list)

    else:
        morphology['entities'] = first_word #FIX TODO
        #morphology['entities'] = extract_named_entities(np_list)

    return morphology

def analyze_possessive_np(poss, np_list):
    '''
    This function is called to analyze possessive constructions like "my name"
    It extracts the person who is possessing and what does the person possess - the category in this case would be "name" and the person possessing is the speaker
    The predicate is created by adding a suffix "-is" to the category e.g. "name-is"
    '''
    #TODO: more complex possessives e.g. "my best friend's name"

    morphology = grammar['possessive'][poss]

    for word in np_list[1:]:
        if word in grammar['categories']:
            morphology['object'] = word
            if morphology['person'] == 'second':
                morphology['subject'] = 'leolani'

            if morphology['person'] == 'first':
                morphology['subject'] = 'speaker'
        else:
            LOG.error('unknown category for possessive: ' + str(np_list))

    morphology['predicate'] = np_list[1] + '-is'

    return morphology

def extract_named_entities(np_list):
    '''
    Using the Stanford NER package, this function tries to extract named entities such as persons, locations, organizations etc.
    '''
    #TODO: BETTER NER FUNCTION

    from nltk.tag import StanfordNERTagger
    ROOT = os.path.join(os.path.dirname(__file__))
    ner = StanfordNERTagger(os.path.join(ROOT, 'stanford-ner', 'english.muc.7class.distsim.crf.ser'),
                            os.path.join(ROOT, 'stanford-ner', 'stanford-ner.jar'), encoding='utf-8')

    recognized_entities = []

    ner_text = ner.tag(np_list)
    LOG.debug('NER: {}'.format(ner_text))

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
    return recognized_entities


def analyze_pronoun(pronoun, speaker):
    '''
    This function returns a morphology which it reads from the grammar (dict.json)
    The grammar has information about person (1st, 2nd, 3rd) and number (singular or plural) for regular and possessive pronouns
    '''
    morphology = {}

    if pronoun in grammar['possessive']:
        morphology = grammar['possessive'][pronoun]

    elif pronoun in grammar['pronouns']:
        morphology = grammar['pronouns'][pronoun]

    else:
        LOG.error('unknown pronoun: '+pronoun)

    return morphology


def analyze_verb(verb):
    '''
    This function is called when a verb is detected, it can be either the verb to be or one of the verbs from the predicate list
    '''
    morphology = {}

    if verb in grammar['to be']:
        morphology['to be'] = grammar['to be'][verb]

    else:
        if verb.endswith('s'):
            morphology['person']='third'

        verb_lemma = wnl.lemmatize(verb, pos='v')
        if verb_lemma in grammar['verbs']:
           morphology['predicate'] = verb_lemma+'s'
        else:
            LOG.error('unkown verb: '+verb+', lemma: '+verb_lemma)

    return morphology


def analyze_wh_question(words, speaker, response_type, viewed_object):
    '''
    This function analyzes questions which start with who, what, where (why and when are also in this category but are not yet comprehended by Leolani)

    '''
    tagged = pos_tag(words)
    rdf = {'subject': '', 'predicate': '', 'object': ''}


    if words[1].strip() in grammar['to be']:
        to_be = words[1].strip()
        morphology = grammar['to be'][to_be]

    elif words[1].strip() in grammar['verbs'].keys()+grammar['predicates']+grammar["modal_verbs"]:
        rdf['predicate'] = words[1].strip()
        if rdf['predicate'] not in grammar['modal_verbs']:
            for w in words[2:]:
                if w not in ['a', 'the']: rdf['object'] += w+' '

    else:
        LOG.error("I seem to have misunderstood the word "+words[1].strip()+" in your question")
        return

    if len(words)<3 :
        LOG.error("Too few words in this question")
        return

    third_word = words[2].lower().strip()
    third_pos = pos_tag([third_word])[0][1]

    if third_pos in ['PRP$', 'NN','PRP','NNS']:
        np = [third_word]

        for pos in tagged[3:]:
            if pos[1] == 'IN':  # where are you FROM
                if pos[0] == 'from': rdf['predicate'] = 'is_from'
                break
            elif not pos[1].startswith('V'):
                np.append(pos[0])

        np_info = analyze_np(np, speaker)
        rdf = pack_rdf_from_np_info(np_info, speaker, rdf)

        if len(words)>3 and wnl.lemmatize(words[3].lower().strip(), 'v') in grammar['verbs']:
            verb_info = analyze_verb(words[3].lower().strip())
            if 'predicate' in verb_info.keys():
                rdf['predicate'] = verb_info['predicate']

        if len(words) > 3 and wnl.lemmatize(words[3].lower().strip(), 'v') =='see': #what do you see
            rdf['predicate'] = 'sees'

    elif third_pos == 'IN':
        if third_word == 'from':
            rdf['predicate'] = 'is_from'
            for word in words[3:]:
                rdf['object'] += (word + ' ')

    else:
        LOG.error("This word "+third_word+" is surprising me")

    LOG.debug('analysis of wh-question produced this rdf: {}'.format(rdf))
    return rdf


def analyze_verb_question(words, speaker, viewed_objects):
    '''
    This function analyzes questions which start with a verb to be or a modal verb
    '''
    tagged = pos_tag(words)
    rdf = {'subject': '', 'predicate': '', 'object': ''}

    # extract subject
    np, index = extract_np(words, tagged, index=1)
    np_info = analyze_np(np, speaker)

    if 'pronoun' in np_info and 'person' in np_info['pronoun']:
        if np_info['pronoun']['person'] == 'second':
            rdf['subject'] = 'leolani'
        elif np_info['pronoun']['person'] == 'first':
            rdf['subject'] = speaker

    if 'human' in np_info:
        rdf['subject'] = np_info['human']
    if not len(np_info):
        LOG.error('issue  with extracting noun phrase:' + str(np))
        return ('Sorry, I am confused')

    verb = words[index + 1]
    verb_info = analyze_verb(verb)

    print("VERB", verb, str(verb_info))

    if 'predicate' in verb_info:
        rdf['predicate'] = verb_info['predicate']  # 'knows' instead of 'know' - predicate mapping

    rdf['object'] = words[index + 2:]
    return rdf
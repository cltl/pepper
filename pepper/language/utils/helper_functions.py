from __future__ import unicode_literals

from pepper import logger

from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

from datetime import date
import json
import re
import os
from pepper.language.utils.analyzers_old import analyze_np

import urllib2, urllib
import traceback, sys

LOG = logger.getChild(__name__)

wnl = WordNetLemmatizer()

ROOT = os.path.join(os.path.dirname(__file__), '..')
json_dict = json.load(open(os.path.join(ROOT, 'data', 'lexicon.json')))
grammar = json_dict

names = ['selene', 'bram', 'leolani', 'piek', 'selene', 'lenka']
statements = [['my favorite food is cake', 'lenka'], ['I know Bram', 'Piek'],
              ['My name is lenka', 'person'],
              ['i like action movies', 'bram'], ['bram likes romantic movies', 'selene'],
              ['bram is from Italy', 'selene']]  # [question, speaker]
questions = [['where is selene from?', 'jo'], ['what does piek like?', 'jo'], ['What is your name', 'person'],
             ['who knows bram?', 'ji'],
             ['who likes soccer?', 'selene'],
             ['who is from italy?', 'jill'], ['where are you from', 'person'], ['who do i know?', 'bram'],
             ['where do you live?', 'person']]


# ['Have you ever met Michael Jordan?', 'piek'], ['Has Selene ever met piek', 'person'], ['Does Selene know piek', 'bram'],
# ['Does bram know Beyonce', 'person'], ['Do you know me','bram']]

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
        print(word + ' - ' + s.lemmas()[0].name() + ': ' + s.definition())
        print(s.lemmas()[0].antonyms())


def extract_np(words, tagged, index):
    '''
    This function extracts a list of non-verbs (np = noun phrase)
    '''
    np = words[index]
    for pos in tagged[index + 1:]:
        if (not pos[1].startswith('V') and (not pos[0] in ['like'])) or (pos[0] in names):
            np += ' ' + pos[0]
            index += 1
        else:
            break
    return np, index


def extract_roles_from_statement(words, speaker, viewed_objects):
    rdf = {'subject': '', 'predicate': '', 'object': ''}
    pos_list = pos_tag(words)
    i = 0

    # OBJECT DETECTION SENTENCE
    if pos_list[0][0] in ['there', 'this', 'it', 'that']:
        if pos_list[1][0] in grammar['to be']:

            if pos_list[2][0] in grammar['possessive']:
                morph = analyze_np(words[2:], speaker)
                # print(morph)
                if morph['predicate'].endswith('-is'):
                    rdf['predicate'] = 'owns'
                    rdf['object'] = morph['predicate'][:-3]
                    if morph['person'] == 'first':
                        rdf['subject'] = speaker
                    elif morph['person'] == 'second':
                        rdf['subject'] = 'leolani'
            else:
                rdf['subject'] = speaker
                rdf['predicate'] = 'sees'
                for word in words[2:]:
                    if word in ['no', 'not']:
                        rdf['predicate'] = 'sees-not'
                    elif word != 'a':  # does it matter which objects leolani sees?
                        rdf['object'] += (word + ' ')

    elif len(pos_list) > 2 and pos_list[2][0] == 'see':
        if pos_list[1][0] == 'can':
            rdf['predicate'] = 'sees'

        elif pos_list[1][0] in ['can\'t', 'cannot', 'don\'t']:
            rdf['predicate'] = 'sees-not'

        if pos_list[0][0].lower() == 'i':
            rdf['subject'] = speaker

        for word in words[3:]:
            if word != 'a':
                rdf['object'] += (word + ' ')
    else:
        for pos in pos_list:
            if pos[1].startswith('V') or wnl.lemmatize(words[i]) in grammar['verbs']:
                if pos_list[i + 1] and pos_list[i + 1][0] == 'from':
                    rdf['predicate'] = 'is_from'
                    i += 1
                else:
                    rdf['predicate'] = words[i] + 's' if not words[i].endswith('s') else words[i]
                    if rdf['predicate'] == 'cans': rdf['predicate'] = 'can'
                    if rdf['predicate'] == 'haves': rdf['predicate'] = 'owns'
                break
            rdf['subject'] += (words[i] + ' ')
            i += 1
        for word in words[i + 1:]:
            rdf['object'] += (word + ' ')
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
    if 'pronoun' in dict:
        dict = dict['pronoun']
    if 'person' in dict:
        if dict['person'] == 'first':
            return speaker
        elif dict['person'] == 'second':
            return 'leolani'


def dereference_pronouns(self, rdf, grammar, speaker):
    for el in rdf:
        if len(rdf[el].split()) > 1:
            pos = rdf[el].split()[0]
            rest = rdf[el].split()[1]
            for w in rdf[el].split()[2:]:
                rest += '-' + w

            l = find(pos, self.GRAMMAR)
            #print('deref ',pos,l)
            if l and 'person' in l:
                #print('dereferencing ', l)

                rdf[el] = fix_pronouns(l, speaker)
                rdf['predicate'] = rest + '-is'
                if l['person']=='second':
                    rdf['object'] = rdf['subject']
                    rdf['subject'] = 'leolani'

                    '''
                    if rdf['subject']=='':
                    '''
                elif l['person']=='first':
                    rdf['object'] = rdf['subject']
                    rdf['subject']=speaker


                break

        else:
            rdf[el] = rdf[el].strip()
            if rdf[el].lower() in grammar['pronouns']['subject']:
                dict = {}
                dict['pronoun'] = grammar['pronouns']['subject'][rdf[el].lower()]

                if dict['pronoun']['person'] == 'third':
                    if len(self.chat.utterances) > 2:
                        print(self.chat.utterances[-2].parser.constituents)
                    else:
                        print('Which ' + rdf[el] + ' do you mean?')
                else:
                    rdf[el] = fix_pronouns(dict, speaker)
    return rdf


from nltk.stem import WordNetLemmatizer


def lemmatize(word, tag=''):
    lemmatizer = WordNetLemmatizer()
    lem = ''
    if len(word.split()) > 1:
        for el in word.split():
            lem += lemmatizer.lemmatize(el) + ' '
        return lem.strip()
    if tag != '':
        return lemmatizer.lemmatize(word, tag)
    return lemmatizer.lemmatize(word)


def get_node_label(tree, word):
    label = ''
    for el in tree:
        for node in el:
            if word == node.leaves()[0]:
                label = node.label()
    return label


def find(word, lexicon, typ=None):
    """ Look up and return features of a given word in the lexicon. """

    # Define pronoun categories.
    pronouns = lexicon["pronouns"]
    subject_pros = pronouns["subject"]
    object_pros = pronouns["object"]
    possessive_pros = pronouns["possessive"]
    dep_possessives = possessive_pros["dependent"]
    indep_possessives = possessive_pros["independent"]
    reflexive_pros = pronouns["reflexive"]
    indefinite_pros = pronouns["indefinite"]
    indefinite_person = indefinite_pros["person"]
    indefinite_place = indefinite_pros["place"]
    indefinite_thing = indefinite_pros["thing"]

    # Define verbal categories.
    verbs = lexicon["verbs"]
    to_be = verbs["to be"]
    aux_verbs = verbs["auxiliaries"]
    to_do = aux_verbs["to do"]
    modals = aux_verbs["modals"]
    lexicals = verbs["lexical verbs"]

    # Define determiner categories.
    determiners = lexicon["determiners"]
    articles = determiners["articles"]
    demonstratives = determiners["demonstratives"]
    possessive_dets = determiners["possessives"]
    quantifiers = determiners["quantifiers"]
    wh_dets = determiners["wh-determiners"]
    numerals = determiners["numerals"]
    cardinals = numerals["cardinals"]
    ordinals = numerals["ordinals"]
    s_genitive = determiners["s-genitive"]

    # Define conjunction categories.
    conjunctions = lexicon["conjunctions"]
    coordinators = conjunctions["coordinating"]
    subordinators = conjunctions["subordinating"]

    # Define a question word category.
    question_words = lexicon["question words"]

    # Define a kinship category.
    kinship = lexicon["kinship"]

    if typ == 'verb':
        categories = [to_be,
                      to_do,
                      modals,
                      lexicals]

    elif typ == 'pos':
        categories = [dep_possessives]

    elif typ == 'to_be':
        categories = [to_be]

    elif typ == 'aux':
        categories = [to_be, to_do]
    else:
        categories = [subject_pros,
                      object_pros,
                      dep_possessives,
                      indep_possessives,
                      reflexive_pros,
                      indefinite_person,
                      indefinite_place,
                      indefinite_thing,
                      to_be,
                      to_do,
                      modals,
                      lexicals,
                      articles,
                      demonstratives,
                      possessive_dets,
                      quantifiers,
                      wh_dets,
                      cardinals,
                      ordinals,
                      s_genitive,
                      coordinators,
                      subordinators,
                      question_words,
                      kinship]

    # print("looking up: ", word)

    for category in categories:
        for item in category:
            if word == item:
                return category[item]
    return None


def dbp_query(q, epr, f='application/json'):
    try:
        params = {'query': q}
        params = urllib.urlencode(params)
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(epr + '?' + params)
        request.add_header('Accept', f)
        request.get_method = lambda: 'GET'
        url = opener.open(request)
        return url.read()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise e


def get_uri(string):
    query = "\
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> \
    SELECT ?x \
    WHERE { ?x rdfs:label ?string . \
        FILTER ( ?string = \"" + string + "\" ) }\
    LIMIT 200"
    results = dbp_query(query, "http://dbpedia.org/sparql")
    results = json.loads(results)
    uris = []
    for x in results['results']['bindings']:
        uris.append(x['x']['value'])
    if uris:
        return uris[0]
    else:
        return None

from __future__ import unicode_literals

import json
import os
import urllib

from nltk import pos_tag
from nltk import tree as ntree
from nltk.stem import WordNetLemmatizer

import wordnet_utils as wu
from pepper import logger

LOG = logger.getChild(__name__)

wnl = WordNetLemmatizer()

ROOT = os.path.join(os.path.dirname(__file__), '..')
lexicon = json.load(open(os.path.join(ROOT, 'data', 'lexicon.json')))


def trim_dash(triple):
    """
    :param triple: a set with three elements (subject, object, complement)
    :return: clean triple with extra dashes removed
    """
    for el in triple:
        if triple[el]:
            if triple[el].startswith('-'):
                triple[el] = triple[el][1:]
            if triple[el].endswith('-'):
                triple[el] = triple[el][:-1]
    return triple


def get_triple_element_type(element, forest):
    """
    :param element: text of one element from the triple
    :param forest: parsed tree
    :return: dictionary with semantic types of the element or sub-elements
    """

    types = {}

    if '-' in element:
        text = ''
        for el in element.split('-'):
            text += el + ' '

        text = text.strip()
        uris = get_uris(text)

        # print('LOOKUP: ', text, len(uris))

        # if len(uris) > 0:
        #     print('URI ', text, len(uris))

        # entities with more than 1 uri from DBpedia are NE and collocations
        if len(uris) > 1:
            return 'NE-col'

        # collocations which exist in WordNet
        synsets = wu.get_synsets(text, get_node_label(forest, text))
        if len(synsets):
            typ = wu.get_lexname(synsets)
            return typ + '-col'

        # if entity does not exist in DBP or WN it is considered composite
        for el in element.split('-'):
            types[el] = get_word_type(el, forest)
    else:
        types[element] = get_word_type(element, forest)

    return types


def get_word_type(word, forest):
    """
    :param word: one word from triple element
    :param forest: parsed syntax tree
    :return: semantic type of word
    """

    if word == '':
        return ''

    lexname = get_lexname(word, forest)

    if lexname is not None:
        return lexname

    # words which don't have a lexname are looked up in the lexicon
    entry = lexicon_lookup(word)
    if entry is not None:
        if 'proximity' in entry:
            return 'deictic:' + entry['proximity'] + ',' + entry['number']
        if 'person' in entry:
            return 'pronoun:' + entry['person']
        if 'root' in entry:
            return 'modal:' + str(entry['root'])
        if 'definite' in entry:
            return 'article:' + entry
        if 'integer' in entry:
            return 'numeral:' + entry['integer']

    types = {'NN': 'person', 'V': 'verb', 'IN': 'prep', 'TO': 'prep', 'MD': 'modal'}

    # for words which are not in the lexicon nor have a lexname, the sem.type is derived from the POS tag
    pos = pos_tag([word])[0][1]
    if pos in types:
        return types[pos]

    node = get_node_label(forest, word)
    if node in types:
        return types[node]


def get_lexname(word, forest):
    '''
    :param word: word for which we want a WordNe lexname
    :param forest: parsed forest of the sentence, to extract the POS tag
    :return: lexname of the word
    https://wordnet.princeton.edu/documentation/lexnames5wn
    '''
    if word == '':
        return

    label = get_node_label(forest[0], word)
    if label == '':
        label = pos_tag([word])
        if label == '':
            return None
        label = label[0][1]

    synset = wu.get_synsets(word, label)
    if synset:
        type = wu.get_lexname(synset[0])
        return type

    else:
        return None


def fix_pronouns(pronoun, self):
    """
    :param pronoun: personal ronoun which is said in the sentence
    :param self: Utterance object from which we can get the speaker and lexicon
    :return: disambiguated first or second person pronoun
    In the case of third person pronouns - guesses or asks questions
    * plural *
    """

    speaker = self.chat.speaker
    entry = lexicon_lookup(pronoun, lexicon)

    if entry and 'person' in entry:
        if entry['person'] == 'first':
            return speaker
        elif entry['person'] == 'second':
            return 'leolani'
        else:
            # print('disambiguate third person')
            return pronoun
    else:
        return pronoun


def lemmatize(word, tag=''):
    """
    This function uses the WordNet lemmatizer
    :param word: word to be lemmatized
    :param tag: POS tag of word
    :return: word lemma
    """
    lem = ''
    if len(word.split()) > 1:
        for el in word.split():
            lem += wnl.lemmatize(el) + ' '
        return lem.strip()
    if tag != '':
        return wnl.lemmatize(word, tag)
    return wnl.lemmatize(word)


def get_node_label(tree, word):
    """
    This function extracts POS tag of a word from the parsed syntax tree
    :param tree: syntax tree gotten from initial CFG parsing
    :param word: word whose POS tag we want
    :return: POS tag of the word
    """
    label = ''
    for el in tree:
        for node in el:
            if type(node) == ntree.Tree:
                for subtree in node.subtrees():
                    for n in subtree:
                        if n == word:
                            label = str(subtree.label())
    return label


def lexicon_lookup(word, typ=None):
    """
    Look up and return features of a given word in the lexicon.
    :param word: word which we're looking up
    :param typ: type of word, if type is category then returns the lexicon entry and the word type
    :return: lexicon entry of the word
    """

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
    have = aux_verbs['have']
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
                      have,
                      modals,
                      lexicals]

    elif typ == 'pos':
        categories = [dep_possessives]

    elif typ == 'to_be':
        categories = [to_be]

    elif typ == 'aux':
        categories = [to_do, to_be, have]

    elif typ == 'modal':
        categories = [modals]

    elif typ == 'pronouns':
        categories = [subject_pros,
                      object_pros,
                      dep_possessives,
                      indep_possessives,
                      reflexive_pros,
                      indefinite_person,
                      indefinite_place,
                      indefinite_thing]
    elif typ == 'lexical':
        categories = [lexicals]
    elif typ == 'kinship':
        categories = [kinship]
    elif typ == 'det':
        categories = [articles, demonstratives, possessive_dets, possessive_pros, cardinals, ordinals]
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
                      have,
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

    for category in categories:
        for item in category:
            if word == item:
                if typ == 'category':
                    return category, category[item]
                return category[item]
    return None


def dbp_query(q, base_url, format="application/json"):
    """
    :param q: query for DBpedia
    :param base_url: URL to connect to DBpedia
    :param format: format for query, typically json
    :return: json with DBpedia responses
    """
    params = {
        "default-graph": "",
        "should-sponge": "soft",
        "query": q,
        "debug": "on",
        "timeout": "",
        "format": format,
        "save": "display",
        "fname": ""
    }

    querypart = urllib.urlencode(params)
    response = urllib.urlopen(base_url, querypart).read()
    return json.loads(response)


def get_uris(string):
    """
    :param string: string which we are querying for
    :return: set of URIS from DBpedia for the queried string
    """
    query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                SELECT ?pred WHERE {
                  ?pred rdfs:label """ + "'" + string + "'" + """@en .
                }
                ORDER BY ?pred"""

    try:
        results = dbp_query(query, "http://dbpedia.org/sparql")
        uris = []
        for x in results['results']['bindings']:
            uris.append(x['pred']['value'])
    except:
        uris = []

    return uris

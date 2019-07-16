from __future__ import unicode_literals

import json
import os
import sys
import traceback
import urllib
import urllib2

from nltk import pos_tag
from nltk import tree as ntree
from nltk.stem import WordNetLemmatizer

import wordnet_utils as wu
from pepper import logger

LOG = logger.getChild(__name__)

wnl = WordNetLemmatizer()

ROOT = os.path.join(os.path.dirname(__file__), '..')
lexicon = json.load(open(os.path.join(ROOT, 'data', 'lexicon.json')))

def trim_dash(rdf):
    for el in rdf:
        if rdf[el]:
            if rdf[el].startswith('-'):
                rdf[el] = rdf[el][1:]
            if rdf[el].endswith('-'):
                rdf[el] = rdf[el][:-1]
    return rdf


def get_type(element, forest):
    if '-' in element:
        type = {}
        for el in element.split('-'):
            type[el] = get_lexname(el, forest)
            if type[el]=='None':
                lexicon_category = lexicon_lookup(el,'category')
                type[el]=lexicon_category
    else:
        type = get_lexname(element, forest)
        if type == 'None':
            lexicon_category = lexicon_lookup(element, 'category')
            type = lexicon_category
    return type



def get_lexname(element, forest):
    if element=='':
        return
    label = get_node_label(forest[0], element)
    if label=='':
        #print(element,' has no label')
        label = pos_tag([element])
        #print('NEW LABEL ', label)
        if label=='':
            return None
        label = label[0][1]
    #print(element,label)
    synset = wu.get_synsets(element, label)
    if synset:
        type = wu.get_lexname(synset[0])
        #print('TYPE OF ' + element + ' IS ' + type)
        return type

    else:
        #print(element + ' has no type!')
        return None


def fix_pronouns(pronoun, self):
    """

    :param pronoun:
    :param self:
    :return:
    """
    #print('fixing', dict)
    lexicon = self.LEXICON
    speaker = self.chat.speaker

    dict = lexicon_lookup(pronoun, lexicon)

    if dict and 'person' in dict:
        if dict['person'] == 'first':
            return speaker
        elif dict['person'] == 'second':
            return 'leolani'
        else:
            print('disambiguate third person')
            return pronoun
    else:
        return pronoun


def lemmatize(word, tag=''):
    '''
    :param word:
    :param tag:
    :return:
    '''
    lem = ''
    if len(word.split()) > 1:
        for el in word.split():
            lem += wnl.lemmatize(el) + ' '
        return lem.strip()
    if tag != '':
        return wnl.lemmatize(word, tag)
    return wnl.lemmatize(word)


def get_node_label(tree, word):
    '''
    :param tree:
    :param word:
    :return:
    '''
    label = ''
    if '-' in word:
        word = word.replace('-','')
    for el in tree:
        for node in el:
            if type(node)==ntree.Tree:
                for subtree in node.subtrees():
                    for n in subtree:
                        if n==word:
                            label = str(subtree.label())
    return label



def lexicon_lookup(word, typ=None):
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

    # print("looking up: ", word)

    for category in categories:
        for item in category:
            if word == item:
                if typ=='category':
                    #print(type(category), category)
                    return category, category [item]
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

'''
def dbp_query(q, baseURL, format="application/json"):
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
    response = urllib.urlopen(baseURL, querypart).read()
    return json.loads(response)


def get_uri(string):
    query = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?pred WHERE {
  ?pred rdfs:label """ + "'" + string + "'" + """@en .
}
ORDER BY ?pred"""
    results = dbp_query(query, "http://dbpedia.org/sparql")
    uris = []
    for x in results['results']['bindings']:
        uris.append(x['pred']['value'])
    return uris
'''
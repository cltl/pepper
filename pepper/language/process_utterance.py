from analyzers import *
from theory_of_mind import TheoryOfMind
import random
from time import time

#from pepper.knowledge.theory_of_mind import TheoryOfMind

test_mode = 1 # FOR ADDITIONAL PRINTS

def classify_and_analyze_question(speaker, words, chat_id, chat_turn):
    first_word = words[0].lower().strip()

    if first_word in grammar['question words']:
        response_type = grammar['question words'][first_word]
        rdf = analyze_wh_question(words, speaker, response_type)

    elif first_word in grammar['to be'] or first_word in grammar['modal_verbs']:
        response_type = 'bool'
        rdf = analyze_verb_question(words, speaker)
    else:
        return "Sorry, I did not understand the first word of your question"

    if test_mode: print('RDF extracted from question ', rdf)

    template = write_template(speaker, rdf,chat_id, chat_turn, 'question')
    return template



def analyze_statement(speaker, words, chat_id, chat_turn):

    if '\'' in words[0]:
        words = fix_contractions(words)

    rdf = extract_roles_from_statement(words)
    if rdf['subject'].split()[0].lower() in (grammar['possessive'].keys() + grammar['pronouns'].keys()) or rdf['object'].split()[0].lower() in (grammar['possessive'].keys() + grammar['pronouns'].keys()):
        rdf = dereference_pronouns_for_statement(words, rdf, speaker)

    if test_mode: print('extracted roles from statement', rdf)

    is_rdf_complete  = check_rdf_completeness(rdf)

    if is_rdf_complete!=1:
        return is_rdf_complete

    else:

        template = write_template(speaker, rdf, chat_id, chat_turn,'statement')
        return template






def classify_and_process_utterance(utterance, speaker, chat_id, chat_turn):
    print('--------------------------------------------------------')
    print('utterance: '+utterance+', speaker: '+speaker, 'chat:', chat_id, chat_turn)

    words = tokenize(utterance)
    if words[0] in grammar['question words'].keys()+ grammar['to be'].keys() + grammar['modal verbs']:
        return classify_and_analyze_question(speaker, words, chat_id, chat_turn)
    else:
        return analyze_statement(speaker, words, chat_id, chat_turn)


def analyze_utterance(utterance, speaker, chat_id, chat_turn, brain):
    template = classify_and_process_utterance(utterance, speaker, chat_id, chat_turn)
    if test_mode: print('template for the brain:',template)

    if 'utterance_type' not in template:
        print(template)

    elif template['utterance_type']=='question':
        response = brain.query_brain(template)
        if test_mode: print('brain response to question:', response)
        print(reply_to_question(response))

    elif template['utterance_type']=='statement':
        response = brain.update(template)
        if test_mode: print('brain response to statement:', response)
        print(reply_to_statement(response, speaker))

def run_tests():
    brain = TheoryOfMind()

    chat_turn = 0
    random.seed(time())
    chat_id = int(random.getrandbits(128))

    test_batch = questions

    test_batch2 = [['Who do you know?', 'Piek'],
                  ['You know me', 'Piek'],
                  ['Who do you know?','Piek']] #, ['I know Bram', 'Piek'], ['Who do I know?', 'Bram']]

    test_batch3 = [['you live at the vu','selene'], ['where do you live?', 'bram']]

    for utt in test_batch2:
        analyze_utterance(utt[0], utt[1],chat_id,  chat_turn, brain)
        chat_turn+=1


run_tests()

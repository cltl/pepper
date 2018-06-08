from analyzers import *
from theory_of_mind import TheoryOfMind
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

    if test_mode: print('extracted roles from statement', rdf)

    is_rdf_complete  = check_rdf_completeness(rdf)

    if is_rdf_complete!=1:
        return is_rdf_complete

    else:
        if rdf['subject'].split()[0].lower() in grammar['possessive'].keys()+ grammar['pronouns'].keys():
            rdf = dereference_pronouns(words, rdf, speaker)

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
    chat_id = 0

    test_batch = questions +statements

    for utt in test_batch:
        analyze_utterance(utt[0], utt[1],chat_id,  chat_turn, brain)
        chat_turn+=1


run_tests()

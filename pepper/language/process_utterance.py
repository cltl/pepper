from .analyzers import *

import logging


LOG = logging.getLogger(__name__)


def classify_and_analyze_question(speaker, words, chat_id, chat_turn, viewed_objects):
    '''
    If an utterance is classified as a question, this function is called to determine
    whether it is a wh_ or a verb question (depending on the first word)
    Based on this, we extract an RDF triple of subject-predicate-object, and then pack it in the template
    The template is a json formatted to query the brain
    '''

    first_word = words[0].lower().strip()

    if first_word in grammar['question words']:
        response_type = grammar['question words'][first_word]
        rdf = analyze_wh_question(words, speaker, response_type, viewed_objects)

    elif first_word in grammar['to be'] or first_word in grammar['modal_verbs']:
        rdf = analyze_verb_question(words, speaker, viewed_objects)
    else:
        return "Sorry, I did not understand the first word of your question"

    LOG.info('RDF extracted from question: '+ str(rdf))

    template = write_template(speaker, rdf,chat_id, chat_turn, 'question')

    return template



def analyze_statement(speaker, words, chat_id, chat_turn, viewed_objects):

    '''
    This function analyzes statements, by extracting an rdf
    A complete rdf is stored in the brain, while an incomplete one should raise an error and trigger asking-for-clarification #TODO
    '''

    if '\'' in words[0]:
        words = fix_contractions(words)

    rdf = extract_roles_from_statement(words, speaker, viewed_objects)

    if (rdf['subject'].split() and rdf['subject'].split()[0].lower() in (grammar['possessive'].keys() + grammar['pronouns'].keys())) \
            or (rdf['object'].split() and rdf['object'].split()[0].lower() in (grammar['possessive'].keys() + grammar['pronouns'].keys())):
        rdf = dereference_pronouns_for_statement(words, rdf, speaker)

    LOG.debug('extracted roles from statement', rdf)

    is_rdf_complete = check_rdf_completeness(rdf)

    if not is_rdf_complete:
        LOG.warning('incomplete rdf: {}'.format(rdf))
        return is_rdf_complete

    else:
        template = write_template(speaker, rdf, chat_id, chat_turn, 'statement')
        return template



def classify_and_process_utterance(utterance, speaker, chat_id, chat_turn, viewed_objects):
    '''
     Depending on the first word, the utterance is classified as a question or a statement and then processed accordingly
    '''

    LOG.debug('utterance: '+utterance+', speaker: '+speaker+ ', chat:'+ str(chat_id) +': '+str(chat_turn)+', viewed objects: '+str(viewed_objects))

    words = tokenize(utterance)

    if words[0]=='tell' and words[1]=='me': words = words[2:]
    elif words[0] == 'can' and words[1] == 'you' and  words[2]=='tell' and words[3]=='me': words = words[4:]


    if words[0] in grammar['question words'].keys() + grammar['to be'].keys() + grammar['modal_verbs']:
        return classify_and_analyze_question(speaker, words, chat_id, chat_turn, viewed_objects)
    else:
        return analyze_statement(speaker, words, chat_id, chat_turn, viewed_objects)


def analyze_utterance(utterance, speaker, chat_id, chat_turn, brain, viewed_objects):
    '''
    When the microphone creates a transcript of text-to-speech, this function is the first to be called
    After the utterance is classified and processed, we get a json template to either query the brain or to store it
    The brain returns a response after querying/storing the template
    '''
    template = classify_and_process_utterance(utterance, speaker, chat_id, chat_turn, viewed_objects)
    LOG.info('template for the brain:' + str(template))

    if 'utterance_type' not in template:
        LOG.error('unknown template type: '+str(template))

    elif template['utterance_type']=='question':
        response = brain.query_brain(template)
        LOG.info('brain response to question:' + str(response))

    elif template['utterance_type']=='statement':
        response = brain.update(template)
        LOG.info('brain response to statement:' + str(response))

    return response

def reply(response, speaker):

    '''
    This function is called to generate the response to be said aloud by Leolani
    It needs the response generated from the brain as input, and based on its type (response to question or a statement) it triggers different reply functions
    '''

    if 'statement' in response:
        reply_to_statement(response, speaker)

    elif 'question' in response:
        reply_to_question(response)

    else:
        LOG.error('errouneus brain response: '+ str(response))
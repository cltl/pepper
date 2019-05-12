from pepper.language import *
from pepper.brain import LongTermMemory
from pepper.framework import UtteranceHypothesis, Context, Object, Face
from pepper.language.generation import reply_to_question, reply_to_statement, phrase_thoughts


def fake_context():
    objects = {Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None),
               Object('cat', 0.51, None, None)}
    faces = {Face('Selene', 0.90, None, None, None), Face('Stranger', 0.90, None, None, None)}

    context = Context()
    context.add_objects(objects)
    context.add_people(faces)
    return context


def test():
    #"Suzana enjoys cooking", "Does Suzana enjoy cooking","What does Suzana enjoy", "Selene enjoys cooking","Who enjoys cooking"
    # *** DOES NOT WORK for "Does S love cooking" <- has issues with POS-tags bc. love gets processed as a noun

    #"Selene is from Mexico", "Where is Selene from","Who is from Mexico" <- is_from instead of be_from, but works ok

    # "selene is your friend","who is your friend", "your name is leolani", "what is your name", "my sign is taurus", "what is my sign"

    # "bram owns a laptop", "bram owns two cats", "what does bram own", "who owns two cats"

    # "I have blue eyes", "what do I have", "who has blue eyes"

    # "you can talk", "can you talk","humans can talk", "who can talk", "I must go", "who must go"

    # "you know bram", "do you know bram", "selene knows bram", "does selene know bram"

    # "you know me", "do you know me", "who do you know", "who does selene know" <- THIS DOES NOT WORK ***

    # "you live here", "where do you live" <- WORKS,  but "who lives here", "do you live here" <- DOESN'T

    # "I live in amsterdam", "who lives in amsterdam" <- WORKS,
    # but  "do I live in amsterdam", "where do I live" <- DOESN'T (fuzzy predicate matching?)


    utterances = []
    '''
    utterances_lower = [x.lower() for x in utterances]
    utterances.extend(utterances_lower)
    '''
    chat = Chat("Lenka", fake_context())
    brain = LongTermMemory(
        clear_all=True)  # WARNING! this deletes everything in the brain, must only be used for testing
    for utterance in utterances:
        chat.add_utterance([UtteranceHypothesis(utterance, 1.0)], False)
        chat.last_utterance.analyze()

        if chat.last_utterance.type == language.UtteranceType.QUESTION:
            brain_response = brain.query_brain(chat.last_utterance)
            reply = reply_to_question(brain_response)
        else:
            brain_response = brain.update(chat.last_utterance, reason_types=True)
            # reply = reply_to_statement(brain_response, chat.speaker, brain)
            reply = phrase_thoughts(brain_response, True, True)

        print(chat.last_utterance)
        # if chat.last_utterance.triple is not None:
        #     chat.last_utterance.triple.casefold(format='triple')
        print(chat.last_utterance.triple)
        print(reply)

    return


if __name__ == "__main__":
    test()

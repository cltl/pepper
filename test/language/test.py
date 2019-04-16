from pepper.language import *
from pepper.brain import LongTermMemory
from pepper.framework import UtteranceHypothesis
from pepper.language import utils





def test():
    utterances = ["Who is from London"]#, "I am Bill", "Who am I?"]#,, "I hate rainy weather", "What do I hate?","What do you like?"]
    chat = Chat("Lenka", None)
    brain = LongTermMemory()
    for utterance in utterances:
        chat.add_utterance([UtteranceHypothesis(utterance, 1.0)], False)
        print(utterance)
        template = analyze(chat)

        if type(template)==str:
            print(template)
            break

        elif template["utterance_type"]== language.UtteranceType.QUESTION:
            brain_response = brain.query_brain(template)
            reply = utils.reply_to_question(brain_response, [])
        else:
            brain_response = brain.update(template)
            reply = utils.reply_to_statement(brain_response, chat.speaker, [], brain)

        print(brain_response)

        print(reply)

        print('\n\n')
    return

if __name__ == "__main__":
    test()

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
    utterances = ["What do you like", "You like pizza", "What do you like",
                  "Do you like coffee", "You like coffee", "Do you like coffee",
                  "My favourite animal is cat", "What is my favourite animal",
                  "I own a bottle", "What do I own",
                  "I own a cat", "What do I own"]
    utterances_lower = [x.lower() for x in utterances]
    utterances.extend(utterances_lower)

    chat = Chat("Lenka", fake_context())
    brain = LongTermMemory(
        clear_all=True)  # WARNING! this deletes everything in the brain, must only be used for testing
    for utterance in utterances:
        chat.add_utterance([UtteranceHypothesis(utterance, 1.0)], False)
        chat.last_utterance.analyze()

        x = chat.last_utterance.triple

        if chat.last_utterance.type == language.UtteranceType.QUESTION:
            brain_response = brain.query_brain(chat.last_utterance)
            reply = reply_to_question(brain_response)
        else:
            brain_response = brain.update(chat.last_utterance, reason_types=True)
            # reply = reply_to_statement(brain_response, chat.speaker, brain)
            reply = phrase_thoughts(brain_response, True, True)

        print(chat.last_utterance)
        print(reply)

    return


if __name__ == "__main__":
    test()

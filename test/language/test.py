from pepper.language import *
from pepper.brain import LongTermMemory


#"Newark is not in the Netherlands.","Where are you from?","Do you know Newark?","can you sing?"
def test():
    utterances = ["I hate coffee", "I am from Newark.","this is a chair","you live in this office","I love swimming"]
    chat = Chat("Lenka", None)
    brain = LongTermMemory()
    for utterance in utterances:
        chat.add_utterance(utterance,False)
        print(utterance)
        brain_response = analyze(chat, brain)
        print(brain_response)
        print('\n\n')
    return

if __name__ == "__main__":
    test()

from pepper.language import *
from pepper.brain import LongTermMemory
from pepper.framework import UtteranceHypothesis, Context, Face, Object, Bounds, AbstractImage
from pepper.language.generation import reply_to_question

import numpy as np


def fake_context():

    bounds = Bounds(0, 0, 1, 1)
    image = AbstractImage(np.zeros((100, 100, 3), np.float32), bounds, np.ones((100, 100), np.float32))
    representation = np.zeros(128, np.float32)

    objects = [Object('person', 0.79, bounds, image),]
               # Object('teddy bear', 0.88, None, None),
               # Object('cat', 0.51, None, None)}
    # faces = {Face('Selene', 0.90, None, None, None), Face('Stranger', 0.90, None, None, None)}

    context = Context()
    context.add_objects(objects)
    # context.add_people(faces)
    return context

def load_golden_triples(filename):
    file = open(filename, "r")

    test = file.readlines()
    test_suite = []
    gold = []

    for sample in test:
        rdf = {}
        if sample=='\n':
            break

        #print(sample.split(':')[0],sample.split(':')[1])
        test_suite.append(sample.split(':')[0])
        rdf['subject']= sample.split(':')[1].split()[0].lower()
        rdf['predicate'] = sample.split(':')[1].split()[1].lower()
        if len(sample.split(':')[1].split())>2:
            rdf['object'] = sample.split(':')[1].split()[2].lower()
        else:
            rdf['object']=''

        if len(sample.split(':')) > 2:

            rdf['perspective'] = {}
            rdf['perspective']['certainty'] = float(sample.split(':')[2].split()[0])
            rdf['perspective']['polarity'] = float(sample.split(':')[2].split()[1])
            rdf['perspective']['sentiment'] = float(sample.split(':')[2].split()[2])
            #print('stored perspective ', rdf['perspective'])


        for el in rdf:
            if rdf[el]=='?':
                rdf[el]=''

        gold.append(rdf)

    return test_suite,gold


def load_scenarios(filepath):
    file = open(filepath, "r")
    test = file.readlines()
    scenarios = []

    for sample in test:
        print(sample)
        if sample=='\n':
            break
        scenario = {'statement': '', 'questions': [], 'reply': ''}
        scenario['statement'] = sample.split('-')[0]
        scenario['reply'] = sample.split('-')[2]
        for el in sample.split('-')[1].split(','):
            scenario['questions'].append(el)

        scenarios.append(scenario)

    return scenarios

def compare_triples(triple, gold):
    correct = 0

    if str(triple.predicate) == gold['predicate']:
        correct += 1
    else:
        print('MISMATCH: ', triple.predicate, gold['predicate'])

    if str(triple.subject) == gold['subject']:
        correct += 1
    else:
        print('MISMATCH: ', triple.subject, gold['subject'])

    if str(triple.object) == gold['object']:
        correct += 1
    else:
        print('MISMATCH: ', triple.object, gold['object'])

    return correct


def test_scenario(statement, questions, gold):
    correct = 0
    chat = Chat("Lenka", fake_context())
    brain = LongTermMemory(
        clear_all=True)  # WARNING! this deletes everything in the brain, must only be used for testing

    if ',' in statement:
        for stat in statement.split(','):
            chat.add_utterance([UtteranceHypothesis(stat, 1.0)], False)
            chat.last_utterance.analyze()
            brain.update(chat.last_utterance, reason_types=True)

    else:
        chat.add_utterance([UtteranceHypothesis(statement, 1.0)], False)
        chat.last_utterance.analyze()
        brain.update(chat.last_utterance, reason_types=True)

    for question in questions:
        chat.add_utterance([UtteranceHypothesis(question, 1.0)], False)
        chat.last_utterance.analyze()
        brain_response = brain.query_brain(chat.last_utterance)
        reply = reply_to_question(brain_response)
        print(reply)
        if '-' in reply:
            reply = reply.replace('-',' ')
        if reply.lower().strip()!=gold.lower().strip():
            print('MISMATCH RESPONSE ', reply.lower().strip(), gold.lower().strip())
        else:
            correct+=1

    return correct


def test_scenarios():
    scenarios = load_scenarios("test_files/scenarios.txt")
    correct = 0
    total = 0
    for sc in scenarios:
        correct+=test_scenario(sc['statement'], sc['questions'], sc['reply'])
        total+=len(sc['questions'])
    print(correct, total-correct)


def test_with_triples(path):
    chat = Chat("Lenka", fake_context())
    brain = LongTermMemory(
        clear_all=True)  # WARNING! this deletes everything in the brain, must only be used for testing

    index = 0
    correct = 0
    incorrect = 0
    issues = {}
    test_suite, gold = load_golden_triples(path)

    for utterance in test_suite:
        chat.add_utterance([UtteranceHypothesis(utterance, 1.0)], False)
        chat.last_utterance.analyze()

        if chat.last_utterance.triple==None:
            print(chat.last_utterance,'ERROR')
            incorrect+=3
            index+=1
            issues[chat.last_utterance.transcript] = 'NOT PARSED'
            continue


        t = compare_triples(chat.last_utterance.triple, gold[index])
        if t<3:
            issues[chat.last_utterance.transcript] = t
        correct+=t
        incorrect+=(3-t)

        if chat.last_utterance.type == language.UtteranceType.QUESTION:
            brain_response = brain.query_brain(chat.last_utterance)
            #reply = reply_to_question(brain_response)
            #print(reply)

        else:
            if 'perspective' in gold[index]:
                perspective = chat.last_utterance.perspective
                extracted_perspective={'polarity': perspective.polarity, 'certainty':perspective.certainty, 'sentiment':perspective.sentiment}
                for key in extracted_perspective:
                    if float(extracted_perspective[key])!=gold[index]['perspective'][key]:
                        print('MISMATCH PERSPECTIVE ', key, extracted_perspective[key], gold[index]['perspective'][key])
                        incorrect+=1
                        #print(issues[chat.last_utterance.transcript])
                        #print([extracted_perspective[key], gold[index]['perspective'][key]])
                        issues[chat.last_utterance.transcript] = [extracted_perspective[key], gold[index]['perspective'][key]]
                    else:
                        correct+=1

            '''
            brain_response = brain.update(chat.last_utterance, reason_types=True)
            # reply = reply_to_statement(brain_response, chat.speaker, brain)
            reply = phrase_thoughts(brain_response, True, True)
            '''

        print(chat.last_utterance)
        print(chat.last_utterance.triple)

        #print(reply)
        index+=1

    print(correct, incorrect)
    print('issues ',issues)

    return


if __name__ == "__main__":


    test_files = ["test_files/statements.txt"]

    for test_file in test_files:
        test_with_triples(test_file)

    #test_scenarios()

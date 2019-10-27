from pepper.language import *
from pepper.brain import LongTermMemory
from pepper.framework import UtteranceHypothesis, Context, Face
from pepper.framework.sensor.obj import Object, Bounds
from pepper.language.generation import reply_to_question

import numpy as np


def fake_context():
    # objects = {Object('person', 0.79, None, None), Object('teddy bear', 0.88, None, None),
    #           Object('cat', 0.51, None, None)}
    # faces = {Face('Selene', 0.90, None, None, None), Face('Stranger', 0.90, None, None, None)}

    context = Context()
    # context.add_objects(objects)
    # context.add_people(faces)
    return context


def load_golden_triples(filepath):
    '''
    :param filepath: path to the test file with gold standard
    :return: set with test suite and a set with golden standard
    '''
    file = open(filepath, "r")

    test = file.readlines()
    test_suite = []
    gold = []

    for sample in test:
        triple = {}
        if sample == '\n':
            break

        # print(sample.split(':')[0],sample.split(':')[1])
        test_suite.append(sample.split(':')[0])
        triple['subject'] = sample.split(':')[1].split()[0].lower()
        triple['predicate'] = sample.split(':')[1].split()[1].lower()
        if len(sample.split(':')[1].split()) > 2:
            triple['complement'] = sample.split(':')[1].split()[2].lower()
        else:
            triple['complement'] = ''

        if len(sample.split(':')) > 2:
            triple['perspective'] = {}
            triple['perspective']['certainty'] = float(sample.split(':')[2].split()[0])
            triple['perspective']['polarity'] = float(sample.split(':')[2].split()[1])
            triple['perspective']['sentiment'] = float(sample.split(':')[2].split()[2])
            # print('stored perspective ', triple['perspective'])

        for el in triple:
            if triple[el] == '?':
                triple[el] = ''

        gold.append(triple)

    return test_suite, gold


def load_scenarios(filepath):
    '''
    :param filepath: path to the test file
    :return: dictionary which contains the initial statement, a set of questions, and the golden standard reply
    '''
    file = open(filepath, "r")
    test = file.readlines()
    scenarios = []

    for sample in test:
        print(sample)
        if sample == '\n':
            break
        scenario = {'statement': '', 'questions': [], 'reply': ''}
        scenario['statement'] = sample.split(' - ')[0]
        scenario['reply'] = sample.split(' - ')[2]
        for el in sample.split(' - ')[1].split(','):
            scenario['questions'].append(el)

        scenarios.append(scenario)

    return scenarios


def compare_triples(triple, gold):
    '''
    :param triple: triple extracted by the system
    :param gold: golden triple to compare with
    :return: number of correct elements in a triple
    '''
    correct = 0

    if str(triple.predicate) == gold['predicate']:
        correct += 1
    else:
        print('MISMATCH: ', triple.predicate, gold['predicate'])

    if str(triple.subject) == gold['subject']:
        correct += 1
    else:
        print('MISMATCH: ', triple.subject, gold['subject'])

    if str(triple.complement) == gold['complement']:
        correct += 1
    else:
        print('MISMATCH: ', triple.complement, gold['complement'])

    return correct


def test_scenario(statement, questions, gold):
    '''
    :param statement: one or several statements separated by a comma, to be stored in the brain
    :param questions: set of questions regarding the stored statement
    :param gold: gold standard reply
    :return: number of correct replies
    '''
    correct = 0
    chat = Chat("Lenka", fake_context())
    brain = LongTermMemory(
    clear_all=True)  # WARNING! this deletes everything in the brain, must only be used for testing

    # one or several statements are added to the brain
    if ',' in statement:
        for stat in statement.split(','):
            chat.add_utterance([UtteranceHypothesis(stat, 1.0)], False)
            chat.last_utterance.analyze()
            brain.update(chat.last_utterance, reason_types=True)
    else:
        chat.add_utterance([UtteranceHypothesis(statement, 1.0)], False)
        chat.last_utterance.analyze()
        brain.update(chat.last_utterance, reason_types=True)

    # brain is queried and a reply is generated and compared with golden standard
    for question in questions:
        chat.add_utterance([UtteranceHypothesis(question, 1.0)], False)
        chat.last_utterance.analyze()
        brain_response = brain.query_brain(chat.last_utterance)
        reply = reply_to_question(brain_response)
        print(reply)
        if '-' in reply:
            reply = reply.replace('-', ' ')
        if reply.lower().strip() != gold.lower().strip():
            print('MISMATCH RESPONSE ', reply.lower().strip(), gold.lower().strip())
        else:
            correct += 1

    return correct


def test_scenarios():
    '''
    This functions opens the scenarios test file and runs the test for all the scenarios
    :return: number of correct and number of incorrect replies
    '''
    scenarios = load_scenarios("./data/scenarios.txt")
    correct = 0
    total = 0
    for sc in scenarios:
        correct += test_scenario(sc['statement'], sc['questions'], sc['reply'])
        total += len(sc['questions'])
    print('CORRECT: ', correct, ',\tINCORRECT: ', total - correct)


def test_with_triples(path):
    '''
    This function loads the test suite and gold standard and prints the mismatches between the system analysis of the test suite,
    including perspective if it is added, as well as the number of correctly and incorrectly extracted triple elements
    :param path: filepath of test file
    '''
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

        if chat.last_utterance.triple == None:
            print(chat.last_utterance, 'ERROR')
            incorrect += 3
            index += 1
            issues[chat.last_utterance.transcript] = 'NOT PARSED'
            continue

        t = compare_triples(chat.last_utterance.triple, gold[index])
        if t < 3:
            issues[chat.last_utterance.transcript] = t
        correct += t
        incorrect += (3 - t)

        if chat.last_utterance.type == language.UtteranceType.QUESTION:
            brain_response = brain.query_brain(chat.last_utterance)
            # reply = reply_to_question(brain_response)
            # print(reply)

        else:
            if 'perspective' in gold[index]:
                perspective = chat.last_utterance.perspective
                extracted_perspective = {'polarity': perspective.polarity, 'certainty': perspective.certainty,
                                         'sentiment': perspective.sentiment}
                for key in extracted_perspective:
                    if float(extracted_perspective[key]) != gold[index]['perspective'][key]:
                        print('MISMATCH PERSPECTIVE ', key, extracted_perspective[key], gold[index]['perspective'][key])
                        incorrect += 1
                        # print(issues[chat.last_utterance.transcript])
                        # print([extracted_perspective[key], gold[index]['perspective'][key]])
                        issues[chat.last_utterance.transcript] = [extracted_perspective[key],
                                                                  gold[index]['perspective'][key]]
                    else:
                        correct += 1

            '''
            brain_response = brain.update(chat.last_utterance, reason_types=True)
            # reply = reply_to_statement(brain_response, chat.speaker, brain)
            reply = phrase_thoughts(brain_response, True, True)
            '''

        # print(chat.last_utterance)
        # print(chat.last_utterance.triple)
        # print(reply)
        index += 1

    print(correct, incorrect)
    print('issues ', issues)

    return


if __name__ == "__main__":
    '''
    test files with triples are formatted like so "test sentence : subject predicate complement" 
    multi-word-expressions have dashes separating their elements, and are marked with apostrophes if they are a collocation
    test files with scenarios are formatted like so "statement - question1, question2, etc - reply"
    '''

    all_test_files = ["./data/wh-questions.txt", "./data/verb-questions.txt",
                      "./data/statements.txt", "./data/perspective.txt"]

    test_files = ["./data/statements.txt"]

    # for test_file in test_files:
    #     test_with_triples(test_file)

    test_scenarios()

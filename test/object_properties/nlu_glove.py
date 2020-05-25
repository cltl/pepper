from nlu_baseline import map_observations_to_instances

from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine

import numpy as np

import os
import sqlite3


def find_closest_avg(model, vocab, target, observations):

    target_vec = np.mean([model[token] for token in target.split(' ') if token in vocab], axis=0)
    target_norm = (target_vec - target_vec.min(0)) / target_vec.ptp(0)

    similarity = 0
    closest_observation = ''

    for observation in observations:
        observation_vec = np.mean([model[token] for token in observation.split(' ') if token in vocab], axis=0)
        observation_norm = (observation_vec - observation_vec.min(0) / observation_vec.ptp(0))
        observation_similarity = 1 - cosine(target_norm, observation_norm)
        if observation_similarity > similarity:
            similarity = observation_similarity
            closest_observation = observation

    return closest_observation


def find_closest_concat(model, vocab, target, observations):

    # TODO: pass the number of dimensions
    num_dims = 100

    # TODO: multi-word objects???
    # Maximum length of color name
    max_color_len = num_dims * 4
    # In clean color names: 309 one-word names, 692 two-word names, 97 three-word names, 1 6-word name
    # TODO: 6-word name = "blue with a hint of purple" --> "purplish blue"
    # num_tokens = len([token for token in target.split(' ')])

    target_norm = pad_name_vec(target, model, vocab, max_color_len)

    similarity = 0
    closest_observation = ''

    for observation in observations:
        observation_norm = pad_name_vec(observation, model, vocab, max_color_len)
        observation_similarity = 1 - cosine(target_norm, observation_norm)
        if observation_similarity > similarity:
            similarity = observation_similarity
            closest_observation = observation

    return closest_observation


def find_closest_wmd(model, target, observations):
    # WMD = Euclidean distance over normalized bag of words (nBOW)
    # "the minimum cumulative distance that all words in document 1 need to travel to exactly match document 2"

    target_list = target.split()

    distance = 1000
    closest_observation = ''

    for observation in observations:
        observation_list = observation.split()
        # WMD automatically removes words that are not in vocabulary
        observation_distance = model.wmdistance(target_list, observation_list)
        if observation_distance < distance:
            distance = observation_distance
            closest_observation = observation

    return closest_observation


def pad_name_vec(description, model, vocab, max_len):

    concat_vec = np.concatenate([model[token] for token in description.split() if token in vocab], axis=0)
    # Pad with zeros if object description has less than 4 tokens
    pad_vec = np.pad(concat_vec, (max_len - len(concat_vec), 0), mode='constant')

    return pad_vec


def find_instance(instance_mapping, observation):
    """
    Find the instance cluster an observation belongs to
    :param instance_mapping:
    :param observation:
    :return:
    """

    instance = 'unknown'
    for key, value in instance_mapping.items():
        if key == observation:
            instance = value

    return instance


def main():
    """

    :return:
    """
    root = './results'
    target_strings = ['dark pink cup', 'black cup', 'blue bottle', 'purple chair', 'red chair', 'blue chair']

    conn = sqlite3.connect('instances.db')
    cur = conn.cursor()
    # cur.execute('CREATE TABLE IF NOT EXISTS nlu_glove (target TEXT, closest TEXT);')

    emb_file = 'glove_to_w2v.6B.100d.txt'
    emb_path = os.path.join('embeddings', emb_file)
    vec_model = KeyedVectors.load(emb_path, mmap='r')
    vocabulary = vec_model.wv.vocab.keys()

    instance_mapping = map_observations_to_instances(cur, root)
    observation_strings = instance_mapping.keys()

    for target_string in target_strings:
        closest_avg = find_closest_avg(vec_model, vocabulary, target_string, observation_strings)
        closest_concat = find_closest_concat(vec_model, vocabulary, target_string, observation_strings)
        closest_wmd = find_closest_wmd(vec_model, target_string, observation_strings)

        avg_instance = find_instance(instance_mapping, closest_avg)
        concat_instance = find_instance(instance_mapping, closest_concat)
        wmd_instance = find_instance(instance_mapping, closest_wmd)

        print('Target string: {}'.format(target_string))
        print('Avg: {}'.format(avg_instance))
        print('Concat: {}'.format(concat_instance))
        print('WMD: {}'.format(wmd_instance))
        print('\n')
        # cur.execute('INSERT INTO nlu_glove VALUES (?, ?);', (str(target_string), str(closest_observation)))

    # conn.commit()
    conn.close()
    # print('\nResults saved to database.')


if __name__ == '__main__':
    main()
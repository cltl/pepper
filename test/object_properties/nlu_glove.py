from nlu_baseline import map_observations_to_instances

from gensim.models import KeyedVectors
from scipy.spatial.distance import cosine

import numpy as np

import os
import sqlite3


def find_closest(model, vocab, target, observations):

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


def main():
    """

    :return:
    """
    root = './results'
    target_strings = ['dark pink cup', 'purple chair']

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
        closest_observation = find_closest(vec_model, vocabulary, target_string, observation_strings)
        # Find the cluster the closest observation belongs to
        for key, value in instance_mapping.items():
            if key == closest_observation:
                closest_instance = value
                print('\nTarget string: {}'.format(target_string))
                print('Closest instance: {}'.format(closest_instance))
        cur.execute('INSERT INTO nlu_baseline VALUES (?, ?);', (str(target_string), str(closest_observation)))

    conn.commit()
    conn.close()
    print('\nResults saved to database.')


if __name__ == '__main__':
    main()
from gensim.models import KeyedVectors
from collections import defaultdict
from scipy.spatial.distance import cosine

import numpy as np

import os


def map_observations_to_instances(root):
    """
    :param root:
    :return:
    """
    # TODO: clean; same function as in nlu_baseline
    string_dict = defaultdict(set)
    for type_dir in (type_dir for type_dir in os.listdir(root)
                     if os.path.isdir(os.path.join(root, type_dir))):
        type_path = os.path.join(root, type_dir)
        for instance_dir in (instance_dir for instance_dir in os.listdir(type_path)
                             if os.path.isdir(os.path.join(type_path, instance_dir))):
            for filename in os.listdir(os.path.join(type_path, instance_dir)):
                file_string = ' '.join(filename.split('_')[:-1])
                string_dict[file_string].add(instance_dir)

    return string_dict


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
    target_string = 'dark pink cup'
    root = './results'

    emb_file = 'glove_to_w2v.6B.100d.txt'
    emb_path = os.path.join('embeddings', emb_file)
    vec_model = KeyedVectors.load(emb_path, mmap='r')
    vocabulary = vec_model.wv.vocab.keys()

    instance_mapping = map_observations_to_instances(root)
    observation_strings = instance_mapping.keys()

    closest_observation = find_closest(vec_model, vocabulary, target_string, observation_strings)

    print('Target string: {}'.format(target_string))
    print('Closest observation: {}'.format(closest_observation))

    # Find the cluster the closest observation belongs to
    # TODO: move to a function (also used in nlu_baseline.py)
    for key, values in instance_mapping.items():
        if key == closest_observation:
            value_list = list(values)
            if len(values) == 1:
                print('I think the object is {}.'.format(value_list[0]))
            else:
                print('I\'m not sure, but I think the object is {} or {}.'.format(value_list[:-1], value_list[-1]))


if __name__ == '__main__':
    main()
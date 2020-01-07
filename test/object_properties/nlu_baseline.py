from fuzzywuzzy import process, fuzz
from collections import defaultdict

import os


def map_observations_to_instances(root):
    """

    :param root:
    :return:
    """
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


def main():
    """

    :return:
    """
    target_string = 'dark pink cup'
    root = './results'

    instance_mapping = map_observations_to_instances(root)
    observation_strings = instance_mapping.keys()

    # Find the observation with minimum edit distance using token sort ratio
    closest_observation = process.extractOne(target_string, observation_strings, scorer=fuzz.token_sort_ratio)

    # Find the cluster the closest observation belongs to
    for key, values in instance_mapping.items():
        if key == closest_observation[0]:
            value_list = list(values)
            if len(values) == 1:
                print('I think the object is {}.'.format(value_list[0]))
            else:
                print('I\'m not sure, but I think the object is {} or {}.'.format(value_list[:-1], value_list[-1]))


if __name__ == '__main__':
    main()
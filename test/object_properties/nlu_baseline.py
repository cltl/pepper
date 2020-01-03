from fuzzywuzzy import process, fuzz
from collections import defaultdict

import os


WORK_DIR = './results/cup'
obj_type = os.path.split(WORK_DIR)[-1]

target_string = 'dark pink cup'

string_dict = defaultdict(set)

for dir in os.listdir(WORK_DIR):
    if os.path.isdir(os.path.join(WORK_DIR, dir)):
        for filename in os.listdir(os.path.join(WORK_DIR, dir)):
            file_string = ' '.join(filename.split('_')[:-1]) + ' ' + obj_type
            string_dict[file_string].add(dir)

observation_strings = set([' '.join(observation_string.split('_')[:-1]) + ' ' + obj_type
                           for observation_string in os.listdir(WORK_DIR)
                           if os.path.isfile(os.path.join(WORK_DIR, observation_string))])

# TODO: deal with cases where there is more than one max value
# The actual observation with minimum edit distance using token sort ration
closest_observation = process.extractOne(target_string, observation_strings, scorer=fuzz.token_sort_ratio)

for key, values in string_dict.items():
    if key == closest_observation[0]:
        value_list = list(values)
        if len(values) == 1:
            reference = value_list[0]
            # The cluster the closest observation belongs to
            print('I think the object is {}'.format(value_list[0]))
        else:
            print('I\'m not sure, but I think the object is {} or {}.'.format(value_list[:-1], value_list[-1]))
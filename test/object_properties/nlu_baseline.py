"""
Generates NLU baseline results and saves them to the database.
"""

import os
import json
import sys
import sqlite3

from fuzzywuzzy import process, fuzz


def map_observations_to_instances(c, root):
    string_dict = dict()
    for type_dir in (type_dir for type_dir in os.listdir(root) if os.path.isdir(os.path.join(root, type_dir))):
        type_path = os.path.join(root, type_dir)
        for instance_dir in (instance_dir for instance_dir in os.listdir(type_path)
                             if os.path.isdir(os.path.join(type_path, instance_dir)) and not instance_dir.endswith('-1')):
            for observation in os.listdir(os.path.join(type_path, instance_dir)):
                c.execute('SELECT color FROM object_info WHERE id = (?)', (str(observation)[:-4],))
                color = c.fetchone()[0]
                string_dict[color + ' ' + type_dir] = instance_dir

    return string_dict


def save_nlu_baseline_results(mode):
    conn = sqlite3.connect('eval_instances.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS nlu_baseline (target TEXT, closest TEXT, true TEXT);')

    instance_mapping = map_observations_to_instances(cur, './results')
    observation_strings = instance_mapping.keys()

    if mode == 'dev':
        target_strings = ['dark pink cup', 'purple chair']
    else:
        with open('./analysis/color_mappings.json') as f:
            target_mapping = json.load(f)
        target_strings = target_mapping.keys()

    for target_string in target_strings:

        # Find the observation with minimum edit distance using token sort ratio
        closest_observation = process.extractOne(target_string, observation_strings, scorer=fuzz.token_sort_ratio)

        # Find the cluster the closest observation belongs to
        for key, value in instance_mapping.items():
            if key == closest_observation[0]:
                closest_instance = value
                if mode == 'eval':
                    print('{}: {} ({})'.format(target_string, closest_instance, target_mapping[target_string]))

                    cur.execute('INSERT INTO nlu_baseline VALUES (?, ?, ?);',
                                (str(target_string), str(closest_instance), target_mapping[target_string]))
                    conn.commit()

                else:
                    print('{}: {}'.format(target_string, closest_instance))

                    cur.execute('INSERT INTO nlu_baseline VALUES (?, ?, ?);',
                                (str(target_string), str(closest_instance), ''))
                    conn.commit()
    conn.close()
    print('\nResults saved to database.')


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('dev', 'eval'):
        print('Usage: python nlu_baseline.py dev or python nlu_baseline.py eval')
    else:
        save_nlu_baseline_results(sys.argv[1])

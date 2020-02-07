from fuzzywuzzy import process, fuzz

import os
import sqlite3


def map_observations_to_instances(c, root):
    """
    """
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


def main():
    """

    :return:
    """
    root = './results'
    target_strings = ['dark pink cup', 'purple chair']

    conn = sqlite3.connect('instances.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS nlu_baseline (target TEXT, closest TEXT);')

    instance_mapping = map_observations_to_instances(cur, root)
    observation_strings = instance_mapping.keys()

    for target_string in target_strings:

        # Find the observation with minimum edit distance using token sort ratio
        closest_observation = process.extractOne(target_string, observation_strings, scorer=fuzz.token_sort_ratio)

        # Find the cluster the closest observation belongs to
        for key, value in instance_mapping.items():
            if key == closest_observation[0]:
                closest_instance = value
                print('{}: {}'.format(target_string, closest_instance))

        cur.execute('INSERT INTO nlu_baseline VALUES (?, ?);', (str(target_string), str(closest_observation)))

    conn.commit()
    conn.close()
    print('\nResults saved to database.')


if __name__ == '__main__':
    main()

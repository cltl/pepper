from sklearn.cluster import DBSCAN

import numpy as np
import os
import sqlite3
import shutil


def read_db(obj_ids):
    """

    :param obj_ids:
    :return:
    """
    conn = sqlite3.connect('instances.db')
    c = conn.cursor()
    query = 'SELECT id, features FROM object_info WHERE id IN ({})'.format(', '.join('?' * len(obj_ids)))
    c.execute(query, obj_ids)
    data = c.fetchall()
    conn.close()

    return data


def get_data(dir_path):
    """

    :param dir_path:
    :return:
    """
    obj_ids = [obj_file[:-4] for obj_file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, obj_file))]
    data = read_db(obj_ids)
    ids = [tup[0] for tup in data]
    feats = np.array([tup[1].strip('[]').split(', ') for tup in data], dtype=float)

    return ids, feats


def cluster_instances(ids, train):
    """

    :param ids:
    :param train:
    :return:
    """
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    db = dbscan.fit(train)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    result = zip(ids, labels)

    return labels, result


def main():
    """

    :return:
    """
    for directory in os.listdir('./results'):
        dir_path = os.path.join('./results', directory)
        print('Processing: {}'.format(dir_path))

        if os.path.isdir(dir_path):
            ids, feats = get_data(dir_path)
            clusters, result = cluster_instances(ids, feats)

            for filename in os.listdir(dir_path):
                for res in result:
                    if res[0] in filename:
                        source = os.path.join(dir_path, str(filename))
                        target = os.path.join(dir_path, directory + '_' + str(res[1]), str(filename))
                        try:
                            shutil.copy(source, target)
                        except IOError:
                            os.makedirs(os.path.join(dir_path, directory + '_' + str(res[1])))
                            shutil.copy(source, target)


if __name__ == '__main__':
    main()

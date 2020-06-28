"""
Clusters object instances.
"""

from sklearn.cluster import DBSCAN

import numpy as np
import os
import sqlite3
import shutil
import math


def read_db(obj_ids):
    conn = sqlite3.connect('eval_instances.db')
    c = conn.cursor()
    data = []
    num_chunks = int(math.ceil(len(obj_ids) / 999))
    for i in range(num_chunks + 1):
        start = i * 999
        if i < num_chunks + 1:
            end = (i + 1) * 999
        else:
            end = len(obj_ids)
        query = 'SELECT id, features FROM object_info[start:end]' \
                'WHERE id IN ({})'.format(', '.join('?' * len(obj_ids[start:end])))
        c.execute(query, obj_ids[start:end])
        chunk_data = c.fetchall()
        data.extend(chunk_data)
    conn.close()

    return data


def get_data(dir_path):
    obj_ids = [obj_file[:-4] for obj_file in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, obj_file))]
    data = read_db(obj_ids)
    ids = [tup[0] for tup in data]
    feats = np.array([tup[1].strip('[]').split(', ') for tup in data], dtype=float)

    return ids, feats


def cluster_instances(ids, train):
    # dbscan = DBSCAN(eps=0.3, min_samples=5)
    dbscan = DBSCAN(eps=0.2, min_samples=3)
    db = dbscan.fit(train)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    result = zip(ids, labels)

    return labels, result


def save_instance_clusters():
    for directory in os.listdir('./results'):
        dir_path = os.path.join('./results', directory)
        print('Processing: {}'.format(dir_path))

        if os.path.isdir(dir_path) and directory == 'bottle':
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
    save_instance_clusters()

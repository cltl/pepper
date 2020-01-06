from sklearn.cluster import DBSCAN

import numpy as np
import os
import sqlite3
import shutil


def cluster_instances(ids, train):

    dbscan = DBSCAN(eps=0.5, min_samples=5)
    db = dbscan.fit(train)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    result = zip(ids, labels)

    return labels, result


def main(work_dir):

    objs = (obj_file for obj_file in os.listdir(work_dir) if os.path.isfile(os.path.join(work_dir, obj_file)))
    obj_ids = [os.path.basename(obj_file)[:-4].split('_')[-1] for obj_file in objs]

    conn = sqlite3.connect('instances.db')
    c = conn.cursor()
    query = 'SELECT id, features FROM features WHERE id IN ({})'.format(', '.join('?' * len(obj_ids)))
    c.execute(query, obj_ids)
    data = c.fetchall()
    ids = [tup[0] for tup in data]
    feats = np.array([tup[1].strip('[]').split(', ') for tup in data], dtype=float)

    clusters, result = cluster_instances(ids, feats)
    for cluster in clusters:
        if not os.path.isdir(os.path.join(work_dir, str(cluster))):
            os.mkdir(os.path.join(work_dir, str(cluster)))

    for item in os.listdir(work_dir):
        for res in result:
            if res[0] in item:
                try:
                    source = os.path.join(work_dir, str(item))
                    target = os.path.join(work_dir, str(res[1]), str(item))
                    shutil.copy(source, target)
                except IOError:
                    print('File not found: {}'.format(item))
                    continue


if __name__ == '__main__':

    for directory in os.listdir('./results'):
        dir_path = os.path.join('./results', directory)
        print('Processing: {}'.format(dir_path))
        if os.path.isdir(dir_path):
            main(dir_path)
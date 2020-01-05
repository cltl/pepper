from classes import ObjectInstance
from util import read_dir, read_object_properties, clustering, dominant_cluster, stats, color_mapping

from matplotlib import colors as mcolors
from matplotlib import pyplot as plt
from datetime import datetime

import os
import re
import sqlite3


ROOT = './data/20190930_133826'
# ROOT = './data/small'
OBJ_HANDLE = "_obj.json"
RGB_HANDLE = "_rgb.png"
DEPTH_HANDLE = "_depth.npy"
META_HANDLE = "_meta.json"


def map_colors():
    """
    Translate matplotlib colors from hex to rgb and edit color names
    :return: dictionary mapping from 1049 matplotlib color names to normalized rgb values
    """

    rgb_mapping = dict()

    for name, value in dict(mcolors.get_named_colors_mapping()).items():
        rgb_value = mcolors.to_rgb(value)
        if name.startswith('xkcd'):
            name = name[5:]
        if name.startswith('tab'):
            name = name[4:]
        if ' urple' in name:
            name = name.replace(' urple', ' purple')
        if 'lavendar' in name:
            name = name.replace('lavendar', 'lavender')
        if 'gray' in name:
            name = name.replace('gray', 'grey')
        # TODO: additional tokenization
        d = re.compile('dark[a-z]+')
        f = d.search(name)
        if f:
            if f.group() not in ('darkish', 'darker'):
                name = re.sub('dark', 'dark ', name)
        l = re.compile('light[a-z]+')
        f = l.search(name)
        if f:
            if f.group() not in ('lightish', 'lighter'):
                name = re.sub('light', 'light ', name)
        m = re.compile('medium[a-z]+')
        f = m.search(name)
        if f:
            name = re.sub('medium', 'medium ', name)
        name = name.replace(' ', '_')
        rgb_mapping[name] = rgb_value

    return rgb_mapping


def save_types(obj, rgb_mapping):
    """
    Save object images to type directories.
    :param obj:
    :param rgb_mapping:
    :return:
    """
    obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img = read_object_properties(obj)
    if obj_confidence < 0.5 or obj_type == 'person':
        return 'id', 'features'
    else:
        obj_instance = ObjectInstance(os.path.basename(obj), obj_type, obj_confidence, obj_bounds,
                                      obj_depth, obj_rgb, obj_img)
        # TODO: image correction?
        result, clusters = clustering(obj_instance.rgb, obj_instance.depth, obj_instance.img)
        dom_cluster = dominant_cluster(result, clusters)
        dom_result = filter(lambda res: res[1] == dom_cluster, result)
        avg_triplet, mode_triplet, median_triplet = stats(dom_result)
        obj_instance.features = avg_triplet + mode_triplet + median_triplet
        obj_instance.color = color_mapping(avg_triplet, rgb_mapping)
        print('{} {}'.format(obj_instance.color, obj_instance.type))

        if not os.path.exists(os.path.join('./results', obj_instance.type)):
            os.mkdir(os.path.join('./results', obj_instance.type))
        plt.savefig('./results/{}/{}_{}_{}'.format(obj_instance.type,
                                                   obj_instance.color, obj_instance.type, obj_instance.id))

        return obj_instance.id, obj_instance.features


def total_count():
    """

    :return:
    """
    img = len([(img_path, objects) for img_path, objects in read_dir(ROOT)])
    obj = len([obj for img_path, objects in read_dir(ROOT) for obj in objects])

    return img, obj


def read_db(c):
    c.execute('SELECT path FROM features')
    paths = c.fetchall()

    return paths


def create_db(c):
    c.execute('CREATE TABLE features(id TEXT, path TEXT, features TEXT);')


def main():

    conn = sqlite3.connect('instances.db')
    c = conn.cursor()
    try:
        known_paths = read_db(c)
    except sqlite3.OperationalError:
        create_db(c)
        known_paths = []

    total_start = datetime.now()

    rgb_mapping = map_colors()

    total_img, total_obj = total_count()
    img_count = 0
    obj_count = 0

    for image, objects in read_dir(ROOT):
        img_count += 1
        for obj_path in objects:
            obj_count += 1
            obj_start = datetime.now()
            print('Processing image {}/{}, object {}/{}.'.format(img_count, total_img, obj_count, total_obj))
            print(obj_path)
            if obj_path in known_paths:
                print('Object already processed: {}.'.format(obj_path))
            else:
                obj_id, obj_features = save_types(obj_path, rgb_mapping)
                if obj_id == 'id':
                    print('Object could not be processed: {}.'.format(obj_path))
                else:
                    c.execute('INSERT INTO features VALUES (?, ?, ?);', (str(obj_id), str(obj_path), str(obj_features)))
                    conn.commit()
            obj_end = datetime.now()
            print('Object processing time: {}'.format(obj_end - obj_start))
            print('Total elapsed time: {}'.format(obj_end - total_start))
            print('\n')

    conn.close()


if __name__ == '__main__':

    main()

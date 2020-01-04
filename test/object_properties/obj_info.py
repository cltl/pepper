from classes import ObjectInstance
from util import read_dir, read_object_properties, clustering, dominant_cluster, stats, color_mapping

from matplotlib import colors as mcolors
from matplotlib import pyplot as plt

import os
import re
import json
from datetime import datetime

# ROOT = './data/20190930_133826'
ROOT = './data/small'
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
        return '', ''
    else:
        obj_instance = ObjectInstance(os.path.basename(obj), obj_type, obj_confidence, obj_bounds,
                                      obj_depth, obj_rgb, obj_img)
        # TODO: image correction?
        result, clusters = clustering(obj_instance.rgb, obj_instance.depth, obj_instance.img)
        dom_cluster = dominant_cluster(result, clusters)
        dom_result = filter(lambda res: res[1] == dom_cluster, result)
        avg_triplet, mode_triplet, median_triplet = stats(dom_result)
        obj_instance.color = color_mapping(avg_triplet, rgb_mapping)
        print('{} {}'.format(obj_instance.color, obj_instance.type))

        if not os.path.exists(os.path.join('./results', obj_instance.type)):
            os.mkdir(os.path.join('./results', obj_instance.type))
        plt.savefig('./results/{}/{}_{}'.format(obj_instance.type, obj_instance.color, obj_instance.id))

        return obj_instance.id, obj_instance.color


def total_count():

    img = len([(img_path, objects) for img_path, objects in read_dir(ROOT)])
    obj = len([obj for img_path, objects in read_dir(ROOT) for obj in objects])

    return img, obj


def main():
    """

    :param id_check:
    :return:
    """

    total_start = datetime.now()

    if os.path.isfile('path_mapping.json'):
        with open('path_mapping.json', 'r') as jsonfile:
            path_dict = json.load(jsonfile)
            known_paths = path_dict.values()
    else:
        path_dict = {}
        known_paths = []

    if os.path.isfile('color_mapping.json'):
        with open('color_mapping.json', 'r') as jsonfile:
            color_dict = json.load(jsonfile)
    else:
        color_dict = {}

    rgb_mapping = map_colors()

    total_img, total_obj = total_count()
    img_count = 0
    obj_count = 0

    for image, objects in read_dir(ROOT):
        img_count +=1
        for obj in objects:
            obj_count +=1
            obj_start = datetime.now()
            print('Processing image {}/{}, object {}/{}.'.format(img_count, total_img, obj_count, total_obj))
            if obj not in known_paths:
                obj_id, obj_color = save_types(obj, rgb_mapping)
                if obj_id and obj_color:
                    path_dict[obj_id] = obj
                    color_dict[obj_id] = obj_color
            else:
                print('Object already processed: {}.'.format(obj))
            obj_end = datetime.now()
            print('Object processing time: {}'.format(obj_end - obj_start))
            print('Total time elapsed: {}'.format(obj_end - total_start))
            print('\n')

    with open('path_mapping.json', 'w') as jsonfile:
        json.dump(path_dict, jsonfile)

    with open('color_mapping.json', 'w') as jsonfile:
        json.dump(color_dict, jsonfile)


if __name__ == '__main__':

    main()

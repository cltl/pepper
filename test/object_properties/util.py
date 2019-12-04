from pepper.framework import AbstractImage, Bounds

from sklearn.cluster import DBSCAN
from matplotlib import colors as mcolors
from scipy.sparse import csr_matrix
from PIL import Image

import numpy as np
import matplotlib.pyplot as plt

import os
import json


OBJ_HANDLE = "_obj.json"
RGB_HANDLE = "_rgb.png"
DEPTH_HANDLE = "_depth.npy"
META_HANDLE = "_meta.json"


def get_depth(path, rgb):
    """
    Read image depth from file or default to zeros if no depth (for images generated from the laptop).
    :param path: image path
    :param rgb: image rgb
    :return:
    """

    if os.path.exists(path + DEPTH_HANDLE):
        depth = np.load(os.path.join(path + DEPTH_HANDLE))
    else:
        depth = np.zeros(rgb.shape[:2])

    return depth


def read_dir(root):
    """
    Read the directory with generated images, objects and associated metadata.
    :param root: directory path
    :return: images and objects in the directory (AbstractImage, object list)
    """

    images = filter(lambda item: os.path.isdir(os.path.join(root, item)), os.listdir(root))

    for image in images:

        img_path = os.path.join(root, image)

        with open(img_path + META_HANDLE) as meta_file:
            img_meta = json.load(meta_file)

        img_rgb = np.array(Image.open(os.path.join(root, image + RGB_HANDLE)))

        img_depth = get_depth(img_path, img_rgb)

        img = AbstractImage(img_rgb, Bounds.from_json(img_meta["bounds"]), img_depth, img_meta["time"])

        objects = [os.path.join(img_path, obj) for obj in os.listdir(img_path)]

        yield img, objects


def object_properties(obj_path):
    """
    Retrieve object data and metadata.
    :param obj_path: object path
    :return: object data and metadata
    """

    with open(os.path.join(obj_path, META_HANDLE[1:])) as meta_file:
        meta_info = json.load(meta_file)

    obj_type = meta_info['name']
    obj_confidence = meta_info['confidence']
    obj_bounds = meta_info['bounds']

    obj_img = Image.open(os.path.join(obj_path, RGB_HANDLE[1:]))

    obj_rgb = np.array(obj_img).astype('float')
    obj_depth = get_depth(obj_path, obj_rgb)

    return obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img


def translate_color():
    """
    Translate matplotlib colors from hex to rgb and return mapping to basic and extended color names.
    :return: mapping to basic and extended color names
    """

    rgb_mapping = dict()

    basic_list = ['black', 'white', 'grey', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown',
                  'teal', 'olive', 'violet', 'turquoise', 'navy']

    for name, value in dict(mcolors.get_named_colors_mapping()).items():

        rgb_value = mcolors.to_rgb(value)

        if name.startswith('xkcd'):
            name = name[5:]
        if name.startswith('tab'):
            name = name[4:]
        if 'gray' in name:
            name = name.replace('gray', 'grey')

        name = name.replace(' ', '_')

        rgb_mapping[name] = rgb_value

    basic_colors, new_mapping = get_basic_colors(basic_list, rgb_mapping)

    return new_mapping, basic_colors


def get_basic_colors(basic_list, rgb_mapping):
    """
    Map more specific color names to basic colors.
    :param basic_list: list of basic colors
    :param rgb_mapping: mapping of rgb values to matplotlib color names
    :return: mapping of extended color names to basic colors, cleaned rgb mapping
    """

    basic_colors = dict.fromkeys(basic_list)
    extended_list = rgb_mapping.keys()  # 1049 color names

    for color in extended_list:

        for basic_color in basic_list:

            if basic_color in color:
                if basic_colors[basic_color]:
                    # TODO: use a set instead?
                    basic_colors[basic_color].append(color)
                else:
                    basic_colors[basic_color] = [color]

            # TODO: add condition if the string contains a substring of color + ish

    uncategorized = count_uncategorized(basic_colors, extended_list)

    for c in uncategorized:
        if 'ruby' in c or 'crimson' in c or 'blood' in c or 'tomato' in c:
            basic_colors['red'].append(c)
        if 'lemon' in c or 'banana' in c:
            basic_colors['yellow'].append(c)
        if 'tangerine' in c:
            basic_colors['orange'].append(c)
        if 'sky' in c or 'sea' in c:
            basic_colors['blue'].append(c)
        if 'kiwi' in c:
            basic_colors['green'].append(c)
        if 'lilac' in c or 'purpl' in c:
            basic_colors['purple'].append(c)
        if 'rose' in c or 'salmon' in c:
            basic_colors['pink'].append(c)
        if 'chocolate' in c or 'coffee' in c:
            basic_colors['brown'].append(c)

    # TODO: check error
    # for uncategorized_color in count_uncategorized(basic_colors, extended_list):
    # del basic_colors[uncategorized_color]

    return basic_colors, rgb_mapping


def count_uncategorized(colordict, colorlist):
    # flatten list of lists and convert to a set because the same specific color can appear under more than one
    # basic color: e.g., green-blue under both green and blue
    colors_in_dict = set(color for colors in colordict.values() for color in colors)
    uncategorized_colors = filter(lambda c: c not in colors_in_dict, colorlist)

    return uncategorized_colors


def clustering(rgb, obj_depth, img):
    """
    Identify clusters within an object bounding box based on color, position and depth.
    :param data: object rgb data
    :param obj_depth: object depth data
    :param img: object image
    :return: pixel-level features and cluster labels, set of identified clusters
    """

    # TODO: make a version without depth
    rgbd = np.dstack((rgb, obj_depth))

    # TODO: check indices
    new_rgbd = csr_matrix(rgbd.reshape(-1, 4))

    dbscan = DBSCAN(eps=5, min_samples=50)
    db = dbscan.fit(new_rgbd)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    labels = db.labels_

    rows, cols, chs = rgbd.shape

    plt.figure(2)
    plt.subplot(2, 1, 1)
    plt.imshow(img)
    plt.axis('off')
    plt.subplot(2, 1, 2)
    plt.imshow(np.reshape(labels, [rows, cols]))
    plt.axis('off')
    # plt.show()

    indices = np.dstack(np.indices(rgbd.shape[:2]))
    rgbxyd = np.concatenate((rgbd, indices), axis=-1)

    result = zip(np.reshape(rgbxyd, [-1, 6]), labels)
    clusters = set([res[1] for res in result])

    return result, clusters


def biggest_cluster(result, clusters):
    """
    Identify the biggest cluster.
    :param result: pixel-level features and cluster labels
    :param clusters: set of identified clusters
    :return: a dictionary with clusters as keys and the corresponding number of pixels as values
    """

    size_dict = dict()

    for cluster in clusters:
        num_relevant = len(filter(lambda res: res[1] == cluster, result))
        size_dict[cluster] = float(num_relevant)

    return size_dict


def closest_cluster(result, clusters):
    """
    Identify the closest cluster based on image depth.
    :param result: pixel-level features and cluster labels
    :param clusters: set of identified clusters
    :return: a dictionary with clusters as keys and their average depth as values
    """
    depth_dict = dict()

    for cluster in clusters:
        relevant = filter(lambda res: res[1] == cluster, result)
        avg_depth = sum([res[0][3] for res in relevant]) / len(relevant)
        depth_dict[cluster] = avg_depth

    return depth_dict


def middle_cluster(result, clusters):
    """
    Identify the cluster closest to the center of the bounding box.
    :param result: pixel-level features and cluster labels
    :param clusters: set of identified clusters
    :return: a dictionary with clusters as keys and their distance from the center as values
    """
    position_dict = dict()

    for cluster in clusters:
        relevant = filter(lambda res: res[1] == cluster, result)

        avg_4 = sum([res[0][4] for res in relevant]) / len(relevant)
        avg_5 = sum([res[0][5] for res in relevant]) / len(relevant)

        diff_4 = (0.5 * max([res[0][4] for res in result]) - avg_4) ** 2
        diff_5 = (0.5 * max([res[0][5] for res in result]) - avg_5) ** 2

        total_diff = diff_4 + diff_5

        position_dict[cluster] = total_diff

    return position_dict


def normalize(dict_data):
    """
    Map dictionary values to the [0, 1] interval.
    :param dict_data: a dictionary with numerical values
    :return: a dictionary with normalized numerical values
    """

    max_val = max(dict_data.values())

    if max_val > 0:
        for key, value in dict_data.items():
            norm_value = value / max_val
            dict_data[key] = norm_value

    return dict_data


def dominant_cluster(result, clusters):
    """
    Identify the dominant cluster in a bounding box based on their size, position and depth.
    :param result: pixel-level features and cluster labels
    :param clusters: a set of identified clusters
    :return: the dominant cluster
    """

    size = biggest_cluster(result, clusters)
    depth = closest_cluster(result, clusters)
    position = middle_cluster(result, clusters)

    normal_size = normalize(size)
    normal_depth = normalize(depth)
    normal_position = normalize(position)

    biggest = max(normal_size, key=normal_size.get)
    closest = min(normal_depth, key=normal_depth.get)
    middle = min(normal_position, key=normal_position.get)

    dom_list = [biggest, closest, middle]

    for cluster in clusters:

        if dom_list.count(cluster) == 3:
            dom_cluster = cluster
            return dom_cluster

        elif dom_list.count(cluster) == 2:
            dom_cluster = cluster
            return dom_cluster

        else:
            dom_cluster = closest
            return dom_cluster


def list_avg(somelist):
    return sum(somelist) / len(somelist)


def separate_rgb_channels(rgb_array):
    r_list = [rgb[0][0] for rgb in rgb_array]
    g_list = [rgb[0][1] for rgb in rgb_array]
    b_list = [rgb[0][2] for rgb in rgb_array]

    return r_list, g_list, b_list


def color_mapping(array, color_names):
    """
    Map object color values to color names.
    :param array: array of rgb values
    :param color_names: dictionary with rgb to color name mapping
    :return: the closest color name for the given rgb array
    """

    r_list, g_list, b_list = separate_rgb_channels(array)

    avg_r = list_avg(r_list)
    avg_g = list_avg(g_list)
    avg_b = list_avg(b_list)

    # normalize the average values because they will be compared with already normalized values
    avg_triplet = (avg_r / 255, avg_g / 255, avg_b / 255)

    min_diff = 1000
    min_key = ''

    for name, color_value in color_names.items():

        r_diff = (avg_triplet[0] - color_value[0]) ** 2
        g_diff = (avg_triplet[1] - color_value[1]) ** 2
        b_diff = (avg_triplet[2] - color_value[2]) ** 2

        total_diff = r_diff + g_diff + b_diff

        if total_diff < min_diff:
            min_diff = total_diff
            min_key = name

    return min_key


def get_surface(obj_bounds):
    """
    Calculate object surface.
    :param obj_bounds: min and max x and y values of the object bounding box
    :return: object bounding box surface area
    """

    x_span = obj_bounds['x1'] - obj_bounds['x0']
    y_span = obj_bounds['y1'] - obj_bounds['y0']

    return 100 * x_span * y_span


def get_size(surface):
    """
    Map object surface to size (tiny/small/big).
    :param surface: object surface area
    :return: tiny/small/big (string)
    """

    if surface < 1:
        size = 'tiny'
    elif surface < 10:
        size = 'small'
    else:
        size = 'big'

    return size
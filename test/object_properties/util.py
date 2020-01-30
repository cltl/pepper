from sklearn.cluster import DBSCAN
from scipy.sparse import csr_matrix
from statistics import mean, mode, median

import numpy as np
import matplotlib.pyplot as plt

import statistics
import re


OBJ_HANDLE = "_obj.json"
RGB_HANDLE = "_rgb.png"
DEPTH_HANDLE = "_depth.npy"
META_HANDLE = "_meta.json"


def clean_color_name(name, keywords):
    """
    Clean matplotlib color names
    :param name:
    :param keywords:
    :param vocab:
    :return:
    """
    name = name.replace('/', ' ')

    if name.startswith('xkcd'):
        name = name[5:]
    if name.startswith('tab'):
        name = name[4:]
    if name.startswith('urple'):
        name = name.replace('urple', 'purple')
    if ' urple' in name:
        name = name.replace(' urple', ' purple')
    if 'purpleish' in name:
        name = name.replace('purpleish', 'purplish')
    if 'lavendar' in name:
        name = name.replace('lavendar', 'lavender')

    left = search_left(name, 'dark', ('darkish', 'darker'))
    if left:
        name = left

    left = search_left(name, 'light', ('lightish', 'lighter'))
    if left:
        name = left

    for mod in ('medium', 'deep', 'hot', 'pale'):
        left = search_left(name, mod)
        if left:
            name = left

    # Add a space between two colors or color and modifier
    for keyword in keywords:
        left = search_left(name, keyword, (keyword + 'ish', keyword + 'y', 'aquamarine', 'blueberry', 'reddy', 'reddish'))
        if left:
            name = left
        right = search_right(name, keyword)
        if right:
            name = right

    return name


def search_left(color_name, color_keyword, word_list=()):

    l = re.compile('{}[a-z]+'.format(color_keyword))
    lf = l.search(color_name)
    if lf:
        if lf.group() not in word_list:
            new_name = color_name.replace(color_keyword, color_keyword + ' ')
            return new_name


def search_right(color_name, color_keyword):

    r = re.compile('[a-z]+{}'.format(color_keyword))
    rf = r.search(color_name)
    if rf:
        new_name = color_name.replace(color_keyword, ' ' + color_keyword)
        return new_name


def detect_objects(rgb, img):
    """
    Identify clusters within an object bounding box based on color, position and depth.
    :param data: object rgb data
    :param obj_depth: object depth data
    :param img: object image
    :return: pixel-level features and cluster labels, set of identified clusters
    """

    new_rgb = csr_matrix(rgb.reshape(-1, 3))

    dbscan = DBSCAN(eps=5, min_samples=50)
    db = dbscan.fit(new_rgb)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True

    labels = db.labels_

    rows, cols, chs = rgb.shape

    plt.figure(2)
    plt.subplot(2, 1, 1)
    plt.imshow(img)
    plt.axis('off')
    plt.subplot(2, 1, 2)
    plt.imshow(np.reshape(labels, [rows, cols]))
    plt.axis('off')

    indices = np.dstack(np.indices(rgb.shape[:2]))
    rgbxy = np.concatenate((rgb, indices), axis=-1)
    result = zip(np.reshape(rgbxy, [-1, 5]), labels)

    return result, set(labels)


def biggest_cluster(result, clusters):
    """
    Identify the biggest cluster.
    :param result: pixel-level features and cluster labels
    :param clusters: set of identified clusters
    :return: a dictionary with clusters as keys and the corresponding number of pixels as values
    """

    size_dict = dict()

    for cluster in clusters:
        num_relevant = len([res for res in result if res[1] == cluster])
        size_dict[cluster] = float(num_relevant)

    return size_dict


def middle_cluster(result, clusters):
    """
    Identify the cluster closest to the center of the bounding box.
    :param result: pixel-level features and cluster labels
    :param clusters: set of identified clusters
    :return: a dictionary with clusters as keys and their distance from the center as values
    """
    position_dict = dict()

    for cluster in clusters:
        relevant = [res for res in result if res[1] == cluster]

        avg_3 = sum([res[0][3] for res in relevant]) / len(relevant)
        avg_4 = sum([res[0][4] for res in relevant]) / len(relevant)

        diff_3 = (0.5 * max([res[0][3] for res in result]) - avg_3) ** 2
        diff_4 = (0.5 * max([res[0][4] for res in result]) - avg_4) ** 2

        total_diff = diff_3 + diff_4
        position_dict[cluster] = total_diff

    return position_dict


def normalize_dict(dict_data):
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
    position_diff = middle_cluster(result, clusters)

    normal_size = normalize_dict(size)
    normal_position_diff = normalize_dict(position_diff)

    cluster_dict = dict()
    for cluster in clusters:
        cluster_dict[cluster] = normal_size[cluster] - normal_position_diff[cluster]

    dom_cluster = max(cluster_dict, key=cluster_dict.get)

    return dom_cluster


def separate_rgb_channels(rgb_array):
    """
    Separate rgb channels and return normalized channels.
    :param rgb_array:
    :return:
    """
    r_list = [rgb[0][0] / 255 for rgb in rgb_array]
    g_list = [rgb[0][1] / 255 for rgb in rgb_array]
    b_list = [rgb[0][2] / 255 for rgb in rgb_array]

    return r_list, g_list, b_list


def manual_mode(a_list):

    max_count = max(a_list.count(item) for item in a_list)
    all_max = [value for value in a_list if a_list.count(value) == max_count]

    return mean(all_max)


def stats(rgb_array):

    r_list, g_list, b_list = separate_rgb_channels(rgb_array)
    mean_rgb = [mean(r_list), mean(g_list), mean(b_list)]
    median_rgb = [median(r_list), median(g_list), median(b_list)]

    try:
        mode_r = mode(r_list)
    except statistics.StatisticsError:
        mode_r = manual_mode(r_list)
    try:
        mode_g = mode(g_list)
    except statistics.StatisticsError:
        mode_g = manual_mode(g_list)
    try:
        mode_b = mode(b_list)
    except statistics.StatisticsError:
        mode_b = manual_mode(b_list)

    mode_rgb = [mode_r, mode_g, mode_b]

    return mean_rgb, mode_rgb, median_rgb


def color_mapping(avg_triplet, color_names):
    """
    Map object color values to color names.
    :param array: array of rgb values
    :param color_names: dictionary with rgb to color name mapping
    :return: the closest color name for the given rgb array
    """

    min_diff = 1000
    min_key = ''

    for color_value, name in color_names.items():
        r_diff = (avg_triplet[0] - color_value[0]) ** 2
        g_diff = (avg_triplet[1] - color_value[1]) ** 2
        b_diff = (avg_triplet[2] - color_value[2]) ** 2
        total_diff = r_diff + g_diff + b_diff

        if total_diff < min_diff:
            min_diff = total_diff
            min_key = name

    return min_key

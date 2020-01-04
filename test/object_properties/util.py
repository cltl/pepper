from pepper.framework import AbstractImage, Bounds

from sklearn.cluster import DBSCAN
from matplotlib import colors as mcolors
from scipy.sparse import csr_matrix
from PIL import Image
from statistics import mean, mode, median

import numpy as np
import matplotlib.pyplot as plt
import statistics

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
    :return: images and objects in the directory (AbstractImage, list)
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


def read_object_properties(obj_path):
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


def clustering(rgb, obj_depth, img):
    """
    Identify clusters within an object bounding box based on color, position and depth.
    :param data: object rgb data
    :param obj_depth: object depth data
    :param img: object image
    :return: pixel-level features and cluster labels, set of identified clusters
    """

    rgbd = np.dstack((rgb, obj_depth))

    # TODO: double-check indices
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

    indices = np.dstack(np.indices(rgbd.shape[:2]))
    rgbxyd = np.concatenate((rgbd, indices), axis=-1)
    result = zip(np.reshape(rgbxyd, [-1, 6]), labels)

    return result, labels


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
    all_max = filter(lambda v: a_list.count(v) == max_count, a_list)

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

    for name, color_value in color_names.items():
        r_diff = (avg_triplet[0] - color_value[0]) ** 2
        g_diff = (avg_triplet[1] - color_value[1]) ** 2
        b_diff = (avg_triplet[2] - color_value[2]) ** 2
        total_diff = r_diff + g_diff + b_diff

        if total_diff < min_diff:
            min_diff = total_diff
            min_key = name

    return min_key

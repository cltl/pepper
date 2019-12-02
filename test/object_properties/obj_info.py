from pepper.framework import AbstractImage, Bounds, Object

from PIL import Image
from sklearn.cluster import DBSCAN
from matplotlib import colors as mcolors
from scipy.sparse import csr_matrix

import numpy as np
import matplotlib.pyplot as plt

import json
import os


def translate_color():
    """
    Translate matplotlib colors from hex to rgb and return mapping to basic and extended color names.
    :return: mapping to basic and extended color names
    """

    rgb_mapping = dict()

    base_list = ['black', 'white', 'grey', 'red', 'green', 'blue', 'yellow', 'orange', 'purple', 'pink', 'brown',
                 'teal', 'olive', 'violet', 'turquoise', 'navy']

    for name, value in dict(mcolors.get_named_colors_mapping()).items():

        rgb_value = mcolors.to_rgb(value)

        if name.startswith('xkcd'):
            name = name[5:]
        if name.startswith('tab'):
            name = name[4:]
        if 'gray' in name:
            name = name.replace('gray', 'grey')

        rgb_mapping[name] = rgb_value

    base_colors, new_mapping = get_base_colors(base_list, rgb_mapping)

    return new_mapping, base_colors


def get_base_colors(base_list, rgb_mapping):
    """
    Map more specific color names to basic colors.
    :param base_list: list of base colors
    :param rgb_mapping: mapping of rgb values to matplotlib color names
    :return: mapping of extended color names to base colors, cleaned rgb mapping
    """

    base_colors = dict.fromkeys(base_list)
    extended_list = rgb_mapping.keys()  # 1049 color names

    for color in extended_list:

        for base_color in base_list:

            if base_color in color:
                if base_colors[base_color]:
                    base_colors[base_color].append(color)
                else:
                    base_colors[base_color] = [color]

    uncategorized = count_uncategorized(base_colors, extended_list)

    for c in uncategorized:
        if 'ruby' in c or 'crimson' in c or 'blood' in c or 'tomato' in c:
            base_colors['red'].append(c)
        if 'lemon' in c or 'banana' in c:
            base_colors['yellow'].append(c)
        if 'tangerine' in c:
            base_colors['orange'].append(c)
        if 'sky' in c or 'sea' in c:
            base_colors['blue'].append(c)
        if 'kiwi' in c:
            base_colors['green'].append(c)
        if 'lilac' in c or 'purpl' in c:
            base_colors['purple'].append(c)
        if 'rose' in c or 'salmon' in c:
            base_colors['pink'].append(c)
        if 'chocolate' in c or 'coffee' in c:
            base_colors['brown'].append(c)

    # TODO: check error
    # for uncategorized_color in count_uncategorized(base_colors, extended_list):
        # del base_colors[uncategorized_color]

    return base_colors, rgb_mapping


def count_uncategorized(colordict, colorlist):

    # flatten list of lists and convert to a set because the same specific color can appear under more than one
    # base color: e.g., green-blue under both green and blue
    colors_in_dict = set(color for colors in colordict.values() for color in colors)
    uncategorized_colors = filter(lambda c: c not in colors_in_dict, colorlist)

    return uncategorized_colors


def read(root):
    """
    Read the directory with generated images, objects and associated metadata.
    :param root: directory path
    :return: images and objects in the directory (AbstractImage, object list)
    """

    images = filter(lambda item: os.path.isdir(os.path.join(root, item)), os.listdir(root))

    for image in images:

        image_path = os.path.join(root, image)

        with open(image_path + META_HANDLE) as meta_file:
            img_meta = json.load(meta_file)

        rgb = np.array(Image.open(os.path.join(root, image + RGB_HANDLE)))

        depth = np.load(os.path.join(root, image + DEPTH_HANDLE))

        img = AbstractImage(rgb, Bounds.from_json(img_meta["bounds"]), depth, img_meta["time"])

        objects = [os.path.join(image_path, obj) for obj in os.listdir(image_path)]

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

    obj_depth = np.load(os.path.join(obj_path, DEPTH_HANDLE[1:]))
    obj_rgb = np.array(obj_img).astype('float')

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
    #plt.show()

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


def main():

    color_names, base_colors = translate_color()

    for image, objects in read(ROOT):

        for obj in objects:

            obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img = object_properties(obj)

            if obj_confidence > 0.5 and obj_type != 'person':

                # TODO: image correction?

                result, clusters = clustering(obj_rgb, obj_depth, obj_img)

                dom_cluster = dominant_cluster(result, clusters)

                dom_result = filter(lambda res: res[1] == dom_cluster, result)

                obj_color = color_mapping(dom_result, color_names)

                obj_surface = get_surface(obj_bounds)
                obj_size = get_size(obj_surface)

                print('{} {} {}'.format(obj_size, obj_color, obj_type))
                plt.savefig(r'./results/{}_{}_{}_{}'.format(os.path.basename(obj), obj_size, obj_color, obj_type))


if __name__ == '__main__':

    ROOT = './data/20190930_133826'
    #ROOT = './data/small'

    OBJ_HANDLE = "_obj.json"
    RGB_HANDLE = "_rgb.png"
    DEPTH_HANDLE = "_depth.npy"
    META_HANDLE = "_meta.json"

    main()
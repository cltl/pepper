from util import *
from classes import ObjectInstance
from matplotlib import colors as mcolors

import glob
import re


def map_colors():
    """
    Translate matplotlib colors from hex to rgb and edit color names
    :return: dictionary mappings from color names to rgb values
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

    color_list = rgb_mapping.keys()  # 1049 color names

    return rgb_mapping, color_list


def main():

    known_ids = [os.path.basename(item)[:-4].split('_')[-1] for item in glob.glob('./results/*/*.png')]
    # TODO: replace translate_color with map_colors
    color_names, basic_colors = translate_color()
    # rgb_mapping, color_list = map_colors()

    for image, objects in read_dir(ROOT):
        for obj in objects:
            if os.path.split(obj)[-1] not in known_ids:
                obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img = read_object_properties(obj)
                if obj_confidence > 0.5 and obj_type != 'person':
                    obj_instance = ObjectInstance(os.path.basename(obj), obj_type, obj_confidence, obj_bounds,
                                                  obj_depth, obj_rgb, obj_img)
                    # TODO: image correction?
                    result, clusters = clustering(obj_instance.rgb, obj_instance.depth, obj_instance.img)
                    dom_cluster = dominant_cluster(result, clusters)
                    dom_result = filter(lambda res: res[1] == dom_cluster, result)
                    avg_triplet, mode_triplet, median_triplet = stats(dom_result)
                    obj_instance.color = color_mapping(avg_triplet, color_names)
                    print('{} {}'.format(obj_instance.color, obj_instance.type))

                    if not os.path.exists(os.path.join('./results', obj_instance.type)):
                        os.mkdir(os.path.join('./results', obj_instance.type))
                    plt.savefig('./results/{}/{}_{}'.format(obj_instance.type, obj_instance.color, obj_instance.id))


if __name__ == '__main__':

    ROOT = './data/20190930_133826'
    #ROOT = './data/small'

    main()
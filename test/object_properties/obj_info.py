from util import *
from classes import ObjectInstance

import glob


def main():

    known_ids = [os.path.basename(item)[:-4].split('_')[-1] for item in glob.glob('./results/*/*.png')]

    color_names, basic_colors = translate_color()

    for image, objects in read_dir(ROOT):

        for obj in objects:

            if os.path.split(obj)[-1] not in known_ids:

                obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img = object_properties(obj)

                if obj_confidence > 0.5 and obj_type != 'person':

                    obj_instance = ObjectInstance(os.path.basename(obj), obj_type, obj_confidence, obj_bounds,
                                                  obj_depth, obj_rgb, obj_img)

                    # TODO: image correction?

                    result, clusters = clustering(obj_instance.rgb, obj_instance.depth, obj_instance.img)

                    dom_cluster = dominant_cluster(result, clusters)

                    dom_result = filter(lambda res: res[1] == dom_cluster, result)

                    obj_instance.color = color_mapping(dom_result, color_names)

                    print('{} {}'.format(obj_instance.color, obj_instance.type))

                    if not os.path.exists(os.path.join('./results', obj_instance.type)):
                        os.mkdir(os.path.join('./results', obj_instance.type))

                    plt.savefig('./results/{}/{}_{}'.format(obj_instance.type, obj_instance.color, obj_instance.id))


if __name__ == '__main__':

    ROOT = './data/20190930_133826'
    #ROOT = './data/small'

    main()
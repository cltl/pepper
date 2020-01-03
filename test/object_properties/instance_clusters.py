from classes import ObjectInstance
from util import *

import shutil


def cluster_instances():

    #   TODO:
    #   2d numpy array containing the clustering features of all object instances in the ObjectInstance class.
    #   Needs to be modified for dealing with multiple types at once.
    train = np.array(ObjectInstance.data())
    dbscan = DBSCAN(eps=0.5, min_samples=5)
    db = dbscan.fit(train)

    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    result = zip(ObjectInstance.all_ids(), labels)

    return labels, result


def main(work_dir):

    # TODO: save the mapping to object instance in obj_info (current files saved post hoc)

    with open('obj_mapping.json', 'r') as jsonfile:
        obj_dict = json.load(jsonfile)
    with open('obj_colors.json', 'r') as jsonfile:
        color_dict = json.load(jsonfile)

    for obj in filter(lambda obj_file: os.path.isfile(os.path.join(work_dir, obj_file)), os.listdir(work_dir)):
        obj_handle = os.path.basename(obj)[:-4].split('_')[-1]
        obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img = read_object_properties(obj_dict[obj_handle])
        obj_instance = ObjectInstance(obj_handle, obj_type, obj_confidence, obj_bounds, obj_depth, obj_rgb, obj_img)
        no_color = len(obj_handle) + 5  # the part of the name without color
        obj_instance.color = os.path.basename(obj)[:-no_color]
        obj_instance.features = color_dict[obj_handle]

    clusters, result = cluster_instances()
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

    WORK_DIR = './results/cup'
    # WORK_DIR = './results/chair'
    main(WORK_DIR)
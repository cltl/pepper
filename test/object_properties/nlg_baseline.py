import os


WORK_DIR = './results/cup'
obj_type = os.path.split(WORK_DIR)[-1]


def get_most_frequent_color(instance_dir):
    instance_dict = dict()
    for observation in os.listdir(os.path.join(WORK_DIR, instance_dir)):
        color = ' '.join(observation.split('_')[:-1])
        if color not in instance_dict:
            instance_dict[color] = 1
        else:
            instance_dict[color] += 1
    most_frequent_color = max(instance_dict, key=instance_dict.get)
    description = most_frequent_color + ' ' + obj_type

    return description


dir_dict = dict()
for instance_dir in filter(lambda el: os.path.isdir(os.path.join(WORK_DIR, el)) and el != '-1', os.listdir(WORK_DIR)):
    instance_description = get_most_frequent_color(instance_dir)
    dir_dict[instance_dir] = instance_description

for key, value in dir_dict.items():
    os.rename(os.path.join(WORK_DIR, key), os.path.join(WORK_DIR, value))

if os.path.isdir(os.path.join(WORK_DIR, '-1')):
    noise_description = get_most_frequent_color('-1')
    os.rename(os.path.join(WORK_DIR, '-1'), os.path.join(WORK_DIR, '{}_1'.format(noise_description)))

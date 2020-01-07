import os


def get_most_frequent_color(type_dir, instance_dir):
    """

    :param type_dir:
    :param instance_dir:
    :return:
    """
    instance_dict = dict()
    obj_type = os.path.split(type_dir)[-1]
    for observation in os.listdir(os.path.join(type_dir, instance_dir)):
        color = ' '.join(observation.split('_'))[:observation.index(obj_type)]
        if color not in instance_dict:
            instance_dict[color] = 1
        else:
            instance_dict[color] += 1
    most_frequent_color = max(instance_dict, key=instance_dict.get)
    description = most_frequent_color + obj_type

    return description


def main():
    """

    :return:
    """

    root = './results'
    for directory in os.listdir(root):
        dir_path = os.path.join(root, directory)
        if os.path.isdir(dir_path):
            dir_dict = dict()
            for instance_dir in filter(lambda el: os.path.isdir(os.path.join(dir_path, el)) and el != '-1',
                                       os.listdir(dir_path)):
                instance_description = get_most_frequent_color(dir_path, instance_dir)
                dir_dict[instance_dir] = instance_description

            for key, value in dir_dict.items():
                os.rename(os.path.join(dir_path, key), os.path.join(dir_path, value))

            if os.path.isdir(os.path.join(dir_path, '-1')):
                noise_description = get_most_frequent_color(dir_path, '-1')
                os.rename(os.path.join(dir_path, '-1'), os.path.join(dir_path, '{}_1'.format(noise_description)))


if __name__ == '__main__':
    main()

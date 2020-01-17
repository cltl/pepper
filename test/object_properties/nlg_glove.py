from matplotlib import colors as mcolors
from gensim.models import KeyedVectors, keyedvectors
from collections import defaultdict, OrderedDict

import numpy as np

import os
import re


def map_colors(keywords, vocab):
    """
    Translate matplotlib colors from hex to rgb
    :return: dictionary mapping from normalized rgb values to 1099 cleaned matplotlib color names
    """

    #   TODO: {name: rgb} changed to {rgb: name}; change in obj_info etc.

    rgb_mapping = dict()

    for name, value in dict(mcolors.get_named_colors_mapping()).items():
        rgb_value = mcolors.to_rgb(value)
        color_name = clean_color_name(name, keywords, vocab)
        rgb_mapping[rgb_value] = color_name

    return rgb_mapping


def clean_color_name(name, keywords, vocab):
    """
    Clean matplotlib color names
    :param name:
    :param keywords:
    :param vocab:
    :return:
    """
    name = name.replace('/', '_').replace(' ', '_')

    if name.startswith('xkcd'):
        name = name[5:]
    if name.startswith('tab'):
        name = name[4:]
    if name == 'urple':
        name = 'purple'  # TODO: check urple
    if ' urple' in name:
        name = name.replace(' urple', '_purple')
    if 'purpleish' in name:
        name = name.replace('purpleish', 'purplish')  # GLOVE embeddings contain purplish but not purpleish
    if 'lavendar' in name:
        name = name.replace('lavendar', 'lavender')
    if 'gray' in name:
        name = name.replace('gray', 'grey')
    # TODO: clean
    d = re.compile('dark[a-z]+')
    f = d.search(name)
    if f:
        if f.group() not in ('darkish', 'darker'):
            name = re.sub('dark', 'dark_', name)
    l = re.compile('light[a-z]+')
    f = l.search(name)
    if f:
        if f.group() not in ('lightish', 'lighter'):
            name = re.sub('light', 'light_', name)
    m = re.compile('medium[a-z]+')
    f = m.search(name)
    if f:
        name = re.sub('medium', 'medium_', name)
    d = re.compile('deep[a-z]+')
    f = d.search(name)
    if f:
        name = re.sub('deep', 'deep_', name)
    h = re.compile('hot[a-z]+')
    f = h.search(name)
    if f:
        name = re.sub('hot', 'hot_', name)
    p = re.compile('pale[a-z]+')
    f = p.search(name)
    if f:
        name = re.sub('pale', 'pale_', name)

    left = search_left(name, keywords)
    if left:
        name = left
    right = search_right(name, keywords)
    if right:
        name = right

    # Up to here: 1951 tokens found in glove vocab, 38 not found

    # This step should not be included for string matching
    for token in name.split('_'):
        if token not in vocab:
            if token.endswith('ish'):
                new_token = token[:-3]
                name = name.replace(token, new_token)
            elif token.endswith('y'):
                new_token = token[:-1]
                name = name.replace(token, new_token)

    # 1964 tokens found in glove vocab, 25 not found

    return name


def search_left(color_name, css_keywords):
    for keyword in css_keywords:
        l = re.compile('{}[a-z]+'.format(keyword))
        lf = l.search(color_name)
        if lf:
            if lf.group() not in (keyword + 'ish', keyword + 'y', 'aquamarine', 'blueberry', 'reddy', 'reddish'):
                new_name = color_name.replace(keyword, keyword + '_')
                return new_name


def search_right(color_name, css_keywords):
    for keyword in css_keywords:
        r = re.compile('[a-z]+{}'.format(keyword))
        rf = r.search(color_name)
        if rf:
            new_name = color_name.replace(keyword, '_' + keyword)
            return new_name


def check_tokens_in_vocab(colors, vocab):
    yes = 0
    no = 0

    for color in colors:
        for el in color.split('_'):
            if el in vocab:
                yes += 1
            else:
                print(el)
                no += 1

    print('\n')
    print('Total YES: {}'.format(yes))
    print('Total NO: {}'.format(no))


def map_instances_to_observations(root):
    """
    :param root:
    :return:
    """
    # TODO: clean; SIMILAR as in nlu_baseline
    string_dict = defaultdict(set)
    for type_dir in (type_dir for type_dir in os.listdir(root)
                     if os.path.isdir(os.path.join(root, type_dir))):
        type_path = os.path.join(root, type_dir)
        for instance_dir in (instance_dir for instance_dir in os.listdir(type_path)
                             if os.path.isdir(os.path.join(type_path, instance_dir)) and not instance_dir.endswith('1')):
            for filename in os.listdir(os.path.join(type_path, instance_dir)):
                color_string = ' '.join(filename.split('_')[:-2])
                string_dict[instance_dir].add(color_string)

    return string_dict


def explore_tokens(color_names, keywords, separator=' '):

    for color_name in color_names:
        tokens = color_name.split(separator)
        new_tokens = ' '.join([check_color(token, keywords) for token in tokens])
        print('{} \t {}'.format(new_tokens, color_name))


def tag_tokens(color_names, keywords, separator=' '):

    all_tags = []

    for color_name in color_names:
        tag_dict = OrderedDict()
        tokens = color_name.split(separator)
        for token in tokens:
            tag_dict[token] = check_color(token, keywords)

        all_tags.append(tag_dict)

    return all_tags


def check_color(token, keywords):
    color = 'NO'
    for keyword in keywords:
        if keyword in token:
            color = 'YES'

    return color


def two_word_nlg():
    pass


def get_keyword_vec(token_list, keywords, model, vocab):

    vecs = []
    for token in token_list:
        if token in vocab:
            vec = model[token]
            vecs.append(vec)
        else:
            for keyword in keywords:
                if keyword in token:
                    vec = model[keyword]
                    vecs.append(vec)

    mean_vec = np.mean(vecs, axis=0, dtype='float32')

    return mean_vec


def main():

    root = './results'

    # TODO: gray vs. grey
    # Some base colors added on top of css keywords
    color_keywords = ['aqua', 'black', 'blue', 'fuchsia', 'gray', 'grey', 'green', 'lime', 'maroon', 'navy', 'olive',
                      'purple', 'red', 'silver', 'teal', 'white', 'yellow', 'brown', 'orange', 'pink', 'turquoise',
                      'lavender', 'magenta']

    emb_file = 'glove_to_w2v.6B.100d.txt'
    emb_path = os.path.join('embeddings', emb_file)

    vec_model = KeyedVectors.load(emb_path, mmap='r')
    vocabulary = vec_model.wv.vocab.keys()

    instance_dict = map_instances_to_observations(root)

    for instance, observations in instance_dict.items():
        print('\n')
        print(instance.upper())
        tags = tag_tokens(list(observations), color_keywords)

        all_yes = [key for tagged in tags for key, value in tagged.items() if value == 'YES']
        if all_yes:
            mean_yes = get_keyword_vec(all_yes, color_keywords, vec_model, vocabulary)
            top_yes = vec_model.most_similar(positive=[mean_yes], topn=1)
        else:
            top_yes = ''

        all_no = [key for tagged in tags for key, value in tagged.items() if value == 'NO']
        if all_no:
            mean_no = np.mean([vec_model[no] for no in all_no if no in vocabulary], axis=0, dtype='float32')
            top_no = vec_model.most_similar(positive=[mean_no], topn=1)
        else:
            top_no = ''

        if top_yes and top_no:
            alt_color = top_no[0][0] + ' ' + top_yes[0][0]
        elif top_yes:
            alt_color = top_yes[0][0]
        else:
            alt_color = top_no[0][0]

        obj_type = instance.split(' ')[-1]

        alt_string = alt_color + ' ' + obj_type

        print(alt_string)

    # TODO: save the mapping in obj_info.py?
    # color_mapping = map_colors(color_keywords, vocabulary)
    # all_colors = color_mapping.values()


if __name__ == '__main__':
    main()
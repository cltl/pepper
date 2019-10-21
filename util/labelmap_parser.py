from nltk.corpus import wordnet
import json


LABELMAP_PATHS = [
    r"C:\Users\Pepper\Documents\Pepper\pepper_tensorflow\pepper_tensorflow\model\coco\labelmap.json",
    r"C:\Users\Pepper\Documents\Pepper\pepper_tensorflow\pepper_tensorflow\model\oid\labelmap.json"
]

MOVING = [wordnet.synset('animal.n.01'), wordnet.synset('clothing.n.01'), wordnet.synset('person.n.01')]
BUILDING = [wordnet.synset('building.n.01')]


def iterate_hypernyms(hypernym_paths):
    for hypernym_path in hypernym_paths:
        for hypernym in hypernym_path:
            yield hypernym

def is_moving(hypernym_paths):
    for hypernym in iterate_hypernyms(hypernym_paths):
        if hypernym in MOVING:
            return True

    return False

def is_building(hypernym_paths):
    for hypernym in iterate_hypernyms(hypernym_paths):
        if hypernym in BUILDING:
            return True

    return False

flatten = lambda l: [item for sublist in l for item in sublist]

object_dict = {}

for path in LABELMAP_PATHS:
    with open(path) as json_file:
        for item in [value['name'] for value in json.load(json_file).values()]:
            synsets = flatten([wordnet.synsets(word, wordnet.NOUN) for word in item.split(" ")])
            hypernym_paths = flatten([synset.hypernym_paths() for synset in synsets])

            object_dict[item] = {
                'moving': is_moving(hypernym_paths),
                'building': is_building(hypernym_paths)
            }

            print('{:25s} {}'.format(item, hypernym_paths))

with open('objects.py', 'w') as python_file:
    python_file.write("OBJECT_INFO = {}".format(object_dict))
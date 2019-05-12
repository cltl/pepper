import os
import re
from datetime import date

from pepper.brain.utils.constants import CAPITALIZED_TYPES


def read_query(query_filename):
    with open(os.path.join(os.path.dirname(__file__), "../queries/{}.rq".format(query_filename))) as fr:
        query = fr.read()
    return query


def is_proper_noun(types):
    return any(i in types for i in CAPITALIZED_TYPES)


def casefold_text(text, format='triple'):
    if format == 'triple':
        return text.strip().lower().replace(" ", "-") if isinstance(text, basestring) else text
    elif format == 'natural':
        return text.strip().lower().replace("-", " ") if isinstance(text, basestring) else text
    else:
        return text


def casefold_capsule(capsule, format='triple'):
    """
    Function for formatting a capsule into triple format or natural language format
    Parameters
    ----------
    capsule:
    format

    Returns
    -------

    """
    for k, v in capsule.items():
        if isinstance(v, dict):
            capsule[k] = casefold_capsule(v, format=format)
        else:
            capsule[k] = casefold_text(v, format=format)

    return capsule


def date_from_uri(uri):
    [year, month, day] = uri.split('/')[-1].split('-')
    return date(int(year), int(month), int(day))


def hash_claim_id(triple):
    return '_'.join(triple)


def confidence_to_certainty_value(confidence):
    if confidence is not None:
        if confidence > .90:
            return 'CERTAIN'
        if confidence > .50:
            return 'PROBABLE'
        if confidence > 0:
            return 'POSIBLE'
    return 'UNDERSPECIFIED'


# def replace_in_file(file, word, word_replacement):
#     pattern = re.compile("<(\d{4,5})>")
#     # ([":])(Unknown)
#
#     for i, line in enumerate(open(file)):
#         for match in re.finditer(pattern, line):
#             print 'Found on line %s: %s' % (i + 1, match.groups())

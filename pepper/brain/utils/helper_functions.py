import os
from datetime import date


def read_query(query_filename):
    with open(os.path.join(os.path.dirname(__file__), "../queries/{}.rq".format(query_filename))) as fr:
        query = fr.read()
    return query


def casefold(text, format='triple'):
    if format == 'triple':
        return text.lower().replace(" ", "_") if isinstance(text, basestring) else text
    elif format == 'natural':
        return text.lower().replace("_", " ") if isinstance(text, basestring) else text
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
            capsule[k] = casefold(v, format=format)

    return capsule


def transform_capsule(capsule):
    """
    Build proper Utterance object from capsule. Step required for proper refactoring
    :param capsule:
    :return:
    """
    pass


def date_from_uri(uri):
    [year, month, day] = uri.split('/')[-1].split('-')
    return date(int(year), int(month), int(day))


def hash_statement_id(triple):
    return '-'.join(triple)

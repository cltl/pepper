import os


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


def hash_statement_id(triple):
    return '-'.join(triple)

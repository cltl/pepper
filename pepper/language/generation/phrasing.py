from pepper.brain.utils.helper_functions import casefold_text

from pepper.language.utils.helper_functions import wnl
from pepper.config import HUMAN_UNKNOWN


def fix_predicate_morphology(subject, predicate, object, format='triple'):
    """
    Conjugation
    Parameters
    ----------
    subject
    predicate

    Returns
    -------

    """
    new_predicate = ''
    if format == 'triple':
        if len(predicate.split()) > 1:
            for el in predicate.split():
                if el == 'is':
                    new_predicate += 'be-'
                else:
                    new_predicate += el + '-'

        elif predicate.endswith('s'):
            new_predicate = wnl.lemmatize(predicate)

        else:
            new_predicate = predicate

    elif format == 'natural':
        if len(predicate.split()) > 1:
            for el in predicate.split():
                if el == 'be':
                    new_predicate += 'is '
                else:
                    new_predicate += el + ' '

        # elif predicate == wnl.lemmatize(predicate):
        #    new_predicate = predicate + 's'

        else:
            new_predicate = predicate

    return new_predicate.strip(' ')


def replace_pronouns(speaker, author=None, entity_label=None, role=None):
    if entity_label is None and author is None:
        return speaker

    if role == 'pos':
        # print('pos', speaker, entity_label)
        if speaker.lower() == entity_label.lower():
            pronoun = 'your'
        elif entity_label.lower() == 'leolani':
            pronoun = 'my'
        else:
            pronoun = entity_label  # third person pos.
        return pronoun

    # Fix author
    elif author is not None:
        if speaker.lower() == author.lower() or author == HUMAN_UNKNOWN:
            pronoun = 'you'
        elif author.lower() == 'leolani':
            pronoun = 'I'
        else:
            pronoun = author.title()

        return pronoun

    # Entity
    if entity_label is not None:
        if speaker.lower() in [entity_label.lower(), 'speaker'] or entity_label == 'Speaker':
            pronoun = 'you'
        elif entity_label.lower() == 'leolani':
            pronoun = 'I'
            '''
        elif entity_label.lower() in ['bram', 'piek']:
            pronoun = 'he' if role == 'subject' else 'him' if role == 'object'  else entity_label
        elif entity_label.lower() in ['selene', 'lenka', 'suzana']:
            pronoun = 'she' if role == 'subject' else 'her'
            '''
        else:
            pronoun = entity_label

        return pronoun

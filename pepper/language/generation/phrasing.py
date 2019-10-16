from pepper.brain.utils.helper_functions import casefold_text


def fix_predicate_morphology(subject, predicate):
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
    for el in predicate.split():
        if el != 'is':
            new_predicate += el + ' '
        else:
            new_predicate += 'are '

    if predicate.endswith('s'): new_predicate = predicate[:-1]

    return new_predicate


def replace_pronouns(speaker, author=None, entity_label=None, role=None):
    if entity_label is None and author is None:
        return speaker

    if role == 'pos':
        print('pos',speaker, entity_label)
        if speaker.lower() == entity_label.lower():
            pronoun = 'your'
        elif entity_label.lower() == 'leolani':
            pronoun = 'my'
        else:
            pronoun = entity_label  # third person pos.
        return pronoun

    elif author is not None:
        if speaker.lower() in [author.lower(), 'speaker'] or author == 'Speaker':
            pronoun = 'you'
        elif author.lower() == 'leolani':
            pronoun = 'I'
        else:
            pronoun = author.title()

        return pronoun

    # Entity
    if entity_label is not None :
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
            pronoun = entity_label.title()

        return pronoun


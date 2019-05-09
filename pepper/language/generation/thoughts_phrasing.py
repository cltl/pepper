import random

from pepper.language.generation.phrasing import *
from pepper.knowledge.sentences import UNDERSTAND, NEW_KNOWLEDGE, EXISTING_KNOWLEDGE, CONFLICTING_KNOWLEDGE, CURIOSITY, \
    HAPPY, TRUST, NO_TRUST


def phrase_all_conflicts(conflicts, speaker=None):
    say = 'I have %s conflicts in my brain.' % len(conflicts)
    conflict = random.choice(conflicts)

    # Conflict of subject
    if len(conflict['objects']) > 1:
        predicate = casefold_text(conflict['predicate'], format='natural')
        options = ['%s %s like %s told me' % (predicate, item['value'], item['author']) for item in conflict['objects']]
        options = ' or '.join(options)
        subject = replace_pronouns(speaker, author=conflict['objects'][1]['author'], entity_label=conflict['subject'],
                                   role='subject')

        say = say + ' For example, I do not know if %s %s' % (subject, options)

    return say


def _phrase_cardinality_conflicts(conflicts, utterance):
    # There is no conflict, so just be happy to learn
    if not conflicts:
        say = random.choice(UNDERSTAND)

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)
        conflict = random.choice(conflicts)
        x = 'you' if conflict.author == utterance.chat_speaker else conflict.author
        y = 'you' if utterance.triple.subject_name == conflict.author else utterance.triple.subject_name

        say += ' %s told me in %s that %s %s %s, but now you tell me that %s %s %s' \
               % (x, conflict.date.strftime("%B"), y, utterance.triple.predicate_name, conflict.object_name,
                  y, utterance.triple.predicate_name, utterance.triple.object_name)

    return say


def _phrase_negation_conflicts(conflicts, utterance):
    # There is no conflict entries, so just be happy to learn
    if not conflicts[0]:
        say = random.choice(NEW_KNOWLEDGE)

    # There is conflict entries
    else:
        affirmative_conflict = [item for item in conflicts if not item.predicate_name.endswith('-not')]
        negative_conflict = [item for item in conflicts if item.predicate_name.endswith('-not')]

        # There is a conflict, so we phrase it
        if affirmative_conflict and negative_conflict:
            say = random.choice(CONFLICTING_KNOWLEDGE)

            affirmative_conflict = random.choice(affirmative_conflict)
            negative_conflict = random.choice(negative_conflict)

            say += ' %s told me in %s that %s %s %s, but in %s %s told me that %s did not %s %s' \
                   % (affirmative_conflict.author, affirmative_conflict.date.strftime("%B"),
                      utterance.triple.subject_name, affirmative_conflict.predicate_name, utterance.triple.object_name,
                      negative_conflict.date.strftime("%B"), negative_conflict.author,
                      utterance.triple.subject_name, affirmative_conflict.predicate_name, utterance.triple.object_name)

        # There is no conflict, so just be happy to learn
        else:
            say = random.choice(NEW_KNOWLEDGE)

    return say


def _phrase_statement_novelty(novelties):
    # I do not know this before, so be happy to learn
    if not novelties:
        say = random.choice(NEW_KNOWLEDGE)

    # I already knew this
    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        novelty = random.choice(novelties)

        say += ' %s told me about it in %s' % (novelty.author, novelty.date.strftime("%B"))

    return say


def _phrase_type_novelty(novelties, utterance):
    entity_role = random.choice(['subject', 'object'])
    entity_label = utterance.triple.subject_name if entity_role == 'subject' else utterance.triple.object_name
    novelty = novelties.subject if entity_role == 'subject' else novelties.object

    entity_label = replace_pronouns(utterance.chat_speaker, entity_label=entity_label, role=entity_role)

    if novelty:
        say = random.choice(NEW_KNOWLEDGE)
        say += ' I have never heard about %s before!' % entity_label

    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        say += ' I know about %s.' % entity_label

    return say


def _phrase_subject_gaps(all_gaps, utterance):
    entity_role = random.choice(['subject', 'object'])
    gaps = all_gaps.subject if entity_role == 'subject' else all_gaps.object

    if entity_role == 'subject':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name)

        else:
            gap = random.choice(gaps)
            say += ' Has a %s ever been %s %s?' % (gap.entity_range_name, gap.predicate_name,
                                                   utterance.triple.subject_name)

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s a %s like %s' % (utterance.triple.predicate_name, utterance.triple.object_name,
                                                        utterance.triple.object_name)

        else:
            gap = random.choice(gaps)
            if '#' in gap.entity_range_name:
                say += ' What is %s %s?' % (utterance.triple.subject_name, gap.predicate_name)
            else:
                say += ' Has %s ever %s a %s?' % (utterance.triple.subject_name, gap.predicate_name,
                                                  gap.entity_range_name)

    return say


def _phrase_object_gaps(all_gaps, utterance):
    # random choice between object or subject
    entity_role = random.choice(['subject', 'object'])
    gaps = all_gaps.subject if entity_role == 'subject' else all_gaps.object

    if entity_role == 'subject':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name)

        else:
            gap = random.choice(gaps)
            say += ' Has any %s %s %s?' % (gap.entity_range_name, gap.predicate_name, utterance.triple.object_name)

    elif entity_role == 'object':
        say = random.choice(CURIOSITY)

        if not gaps:
            types = utterance.triple.object.types_names if utterance.triple.object.types_names != '' else 'things'
            say += ' What types of %s like %s can be %s' % (types, utterance.triple.object_name,
                                                            utterance.triple.predicate_name)

        else:
            gap = random.choice(gaps)
            if '#' in gap.entity_range_name:
                say += ' What is %s %s?' % (utterance.triple.object_name, gap.predicate_name)
            else:
                say += ' What other %s was %s %s?' % (
                gap.entity_range_name, utterance.triple.object_name, gap.predicate_name)

    return say


def _phrase_overlaps(all_overlaps, utterance):
    entity_role = random.choice(['subject', 'object'])
    overlaps = all_overlaps.subject if entity_role == 'subject' else all_overlaps.object

    if not overlaps and entity_role == 'subject':
        say = random.choice(HAPPY)
        say += ' I did not know anything that %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name)

    elif not overlaps and entity_role == 'object':
        say = random.choice(HAPPY)
        say += ' I did not know anybody who %s %s' % (utterance.triple.predicate_name, utterance.triple.object_name)

    elif len(overlaps) < 2 and entity_role == 'subject':
        say = random.choice(HAPPY)

        say += ' Did you know that %s also %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name,
                                                     random.choice(overlaps).entity_name)

    elif len(overlaps) < 2 and entity_role == 'object':
        say = random.choice(HAPPY)

        say += ' Did you know that %s also %s %s' % (random.choice(overlaps).entity_name,
                                                     utterance.triple.predicate_name, utterance.triple.object_name)

    elif entity_role == 'subject':
        say = random.choice(HAPPY)
        sample = random.sample(overlaps, 2)
        say += ' Now I know %s items that %s %s, like %s and %s' % (len(overlaps), utterance.triple.subject_name,
                                                                    utterance.triple.predicate_name,
                                                                    sample[0].entity_name, sample[1].entity_name)

    elif entity_role == 'object':
        say = random.choice(HAPPY)
        sample = random.sample(overlaps, 2)
        types = utterance.triple.object.types_names if utterance.triple.object.types_names != '' else 'things'
        say += ' Now I know %s %s that %s %s, like %s and %s' % (len(overlaps), types,
                                                                 utterance.triple.object_name,
                                                                 utterance.triple.predicate_name,
                                                                 sample[0].entity_name, sample[1].entity_name)

    return say


def phrase_trust(trust):
    if trust == 1:
        say = random.choice(TRUST)
    else:
        say = random.choice(NO_TRUST)

    return say


def phrase_thoughts(update, proactive=True, persist=False):
    """
    Phrase a random thought
    Parameters
    ----------
    update
    proactive
    persist

    Returns
    -------

    """
    # TODO conjugate through fix predicate
    options = ['cardinality_conflicts', 'negation_conflicts', 'statement_novelty', 'entity_novelty']

    if proactive:
        options.extend(['subject_gaps', 'object_gaps', 'overlaps'])

    # Casefold and select approach randomly
    utterance = update['statement']
    utterance.casefold(format='natural')
    thoughts = update['thoughts']
    thoughts.casefold(format='natural')
    approach = random.choice(options)

    if approach == 'cardinality_conflicts':
        say = _phrase_cardinality_conflicts(thoughts.object_conflict(), utterance)

    elif approach == 'negation_conflicts':
        say = _phrase_negation_conflicts(thoughts.negation_conflicts(), utterance)

    elif approach == 'statement_novelty':
        say = _phrase_statement_novelty(thoughts.statement_novelties())

    elif approach == 'entity_novelty':
        say = _phrase_type_novelty(thoughts.entity_novelty(), utterance)

    elif approach == 'subject_gaps':
        say = _phrase_subject_gaps(thoughts.subject_gaps(), utterance)

    elif approach == 'object_gaps':
        say = _phrase_object_gaps(thoughts.object_gaps(), utterance)

    elif approach == 'overlaps':
        say = _phrase_overlaps(thoughts.overlaps(), utterance)

    if persist and say == '':
        say = phrase_thoughts(update, proactive, persist)

    return say

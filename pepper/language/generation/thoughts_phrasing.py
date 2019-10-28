import random

from pepper.language.generation.phrasing import *
from pepper.knowledge.sentences import UNDERSTAND, NEW_KNOWLEDGE, EXISTING_KNOWLEDGE, CONFLICTING_KNOWLEDGE, \
    CURIOSITY, HAPPY, TRUST, NO_TRUST


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
    # There is no conflict, so nothing
    if not conflicts:
        say = None

    # There is a conflict, so we phrase it
    else:
        say = random.choice(CONFLICTING_KNOWLEDGE)
        conflict = random.choice(conflicts)
        x = 'you' if conflict.author == utterance.chat_speaker else conflict.author
        y = 'you' if utterance.triple.subject_name == conflict.author else utterance.triple.subject_name

        # Checked
        say += ' %s told me in %s that %s %s %s, but now you tell me that %s %s %s' \
               % (x, conflict.date.strftime("%B"), y, utterance.triple.predicate_name, conflict.complement_name,
                  y, utterance.triple.predicate_name, utterance.triple.complement_name)

    return say


def _phrase_negation_conflicts(conflicts, utterance):
    # There is no conflict entries, so empty
    if not conflicts or not conflicts[0]:
        say = None

    # There is conflict entries
    else:
        affirmative_conflict = [item for item in conflicts if item.polarity_value == 'POSITIVE']
        negative_conflict = [item for item in conflicts if item.polarity_value == 'NEGATIVE']

        # There is a conflict, so we phrase it
        if affirmative_conflict and negative_conflict:
            say = random.choice(CONFLICTING_KNOWLEDGE)

            affirmative_conflict = random.choice(affirmative_conflict)
            negative_conflict = random.choice(negative_conflict)

            say += ' %s told me in %s that %s %s %s, but in %s %s told me that %s did not %s %s' \
                   % (affirmative_conflict.author, affirmative_conflict.date.strftime("%B"),
                      utterance.triple.subject_name, utterance.triple.predicate_name, utterance.triple.complement_name,
                      negative_conflict.date.strftime("%B"), negative_conflict.author,
                      utterance.triple.subject_name, utterance.triple.predicate_name, utterance.triple.complement_name)

        # There is no conflict, so just be happy to learn
        else:
            say = None

    return say


def _phrase_statement_novelty(novelties, utterance):
    # I do not know this before, so be happy to learn
    if not novelties:
        entity_role = random.choice(['subject', 'complement'])

        say = random.choice(NEW_KNOWLEDGE)

        if entity_role == 'subject':
            if 'person' in utterance.triple.complement.types:
                any_type = 'anybody'
            elif 'location' in utterance.triple.complement.types:
                any_type = 'anywhere'
            else:
                any_type = 'anything'

            # Checked
            say += ' I did not know %s that %s %s' % (any_type, utterance.triple.subject_name,
                                                      utterance.triple.predicate_name)

        elif entity_role == 'complement':
            # Checked
            say += ' I did not know anybody who %s %s' % (utterance.triple.predicate_name,
                                                          utterance.triple.complement_name)

    # I already knew this
    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        novelty = random.choice(novelties)

        # Checked
        say += ' %s told me about it in %s' % (novelty.author, novelty.date.strftime("%B"))

    return say


def _phrase_type_novelty(novelties, utterance):
    entity_role = random.choice(['subject', 'complement'])
    entity_label = utterance.triple.subject_name if entity_role == 'subject' else utterance.triple.complement_name
    novelty = novelties.subject if entity_role == 'subject' else novelties.complement

    if novelty:
        entity_label = replace_pronouns(utterance.chat_speaker, entity_label=entity_label, role=entity_role)
        say = random.choice(NEW_KNOWLEDGE)
        if entity_label != 'you':  # TODO or type person?
            # Checked
            say += ' I had never heard about %s before!' % replace_pronouns(utterance.chat_speaker,
                                                                            entity_label=entity_label,
                                                                            role='complement')
        else:
            say += ' I am excited to get to know about %s!' % entity_label

    else:
        say = random.choice(EXISTING_KNOWLEDGE)
        if entity_label != 'you':
            # Checked
            say += ' I have heard about %s before' % replace_pronouns(utterance.chat_speaker, entity_label=entity_label,
                                                                      role='complement')
        else:
            say += ' I love learning more and more about %s!' % entity_label

    return say


def _phrase_subject_gaps(all_gaps, utterance):
    entity_role = random.choice(['subject', 'complement'])
    gaps = all_gaps.subject if entity_role == 'subject' else all_gaps.complement
    say = None

    if entity_role == 'subject':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name)

        else:
            gap = random.choice(gaps)
            if 'is ' in gap.predicate_name or ' is' in gap.predicate_name:
                say += ' Is there a %s that %s %s?' % (
                    gap.entity_range_name, gap.predicate_name, utterance.triple.subject_name)
            elif ' of' in gap.predicate_name:
                say += ' Is there a %s that %s is %s?' % (
                    gap.entity_range_name, utterance.triple.subject_name, gap.predicate_name)

            elif ' ' in gap.predicate_name:
                say += ' Is there a %s that is %s %s?' % (
                    gap.entity_range_name, gap.predicate_name, utterance.triple.subject_name)
            else:
                # Checked
                say += ' Has %s %s %s?' % (utterance.triple.subject_name, gap.predicate_name, gap.entity_range_name)

    elif entity_role == 'complement':
        say = random.choice(CURIOSITY)

        if not gaps:
            say += ' What types can %s a %s like %s' % (utterance.triple.predicate_name,
                                                        utterance.triple.complement_name,
                                                        utterance.triple.complement_name)

        else:
            gap = random.choice(gaps)
            if '#' in gap.entity_range_name:
                say += ' What is %s %s?' % (utterance.triple.subject_name, gap.predicate_name)
            elif ' ' in gap.predicate_name:
                # Checked
                say += ' Has %s ever %s %s?' % (
                    gap.entity_range_name, gap.predicate_name, utterance.triple.subject_name)

            else:
                # Checked
                say += ' Has %s ever %s a %s?' % (utterance.triple.subject_name, gap.predicate_name,
                                                  gap.entity_range_name)

    return say


def _phrase_complement_gaps(all_gaps, utterance):
    # random choice between complement or subject
    entity_role = random.choice(['subject', 'complement'])
    gaps = all_gaps.subject if entity_role == 'subject' else all_gaps.complement
    say = None

    if entity_role == 'subject':
        say = random.choice(CURIOSITY)

        if not gaps:
            # Checked
            say += ' What types can %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name)

        else:
            gap = random.choice(gaps)  # TODO Lenka/Suzanna improve logic here
            if ' in' in gap.predicate_name:  # ' by' in gap.predicate_name
                say += ' Is there a %s %s %s?' % (
                    gap.entity_range_name, gap.predicate_name, utterance.triple.complement_name)
            else:
                say += ' Has %s %s by a %s?' % (utterance.triple.complement_name,
                                                gap.predicate_name,
                                                gap.entity_range_name)

    elif entity_role == 'complement':
        say = random.choice(CURIOSITY)

        if not gaps:
            otypes = utterance.triple.complement.types_names if utterance.triple.complement.types_names != '' \
                else 'things'
            stypes = utterance.triple.subject.types_names if utterance.triple.subject.types_names != '' else 'actors'
            say += ' What types of %s like %s do %s usually %s' % (otypes, utterance.triple.complement_name, stypes,
                                                                   utterance.triple.predicate_name)

        else:
            gap = random.choice(gaps)
            if '#' in gap.entity_range_name:
                say += ' What is %s %s?' % (utterance.triple.complement_name, gap.predicate_name)
            elif ' by' in gap.predicate_name:
                say += ' Has %s ever %s a %s?' % (
                    utterance.triple.complement_name, gap.predicate_name, gap.entity_range_name)
            else:
                say += ' Has a %s ever %s %s?' % (
                    gap.entity_range_name, gap.predicate_name, utterance.triple.complement_name)

    return say


def _phrase_overlaps(all_overlaps, utterance):
    entity_role = random.choice(['subject', 'complement'])
    overlaps = all_overlaps.subject if entity_role == 'subject' else all_overlaps.complement
    say = None

    if not overlaps:
        say = None

    elif len(overlaps) < 2 and entity_role == 'subject':
        say = random.choice(HAPPY)

        say += ' Did you know that %s also %s %s' % (utterance.triple.subject_name, utterance.triple.predicate_name,
                                                     random.choice(overlaps).entity_name)

    elif len(overlaps) < 2 and entity_role == 'complement':
        say = random.choice(HAPPY)

        say += ' Did you know that %s also %s %s' % (random.choice(overlaps).entity_name,
                                                     utterance.triple.predicate_name, utterance.triple.complement_name)

    elif entity_role == 'subject':
        say = random.choice(HAPPY)
        sample = random.sample(overlaps, 2)

        entity_0 = filter(str.isalpha, str(sample[0].entity_name))
        entity_1 = filter(str.isalpha, str(sample[1].entity_name))

        say += ' Now I know %s items that %s %s, like %s and %s' % (len(overlaps), utterance.triple.subject_name,
                                                                    utterance.triple.predicate_name,
                                                                    entity_0, entity_1)

    elif entity_role == 'complement':
        say = random.choice(HAPPY)
        sample = random.sample(overlaps, 2)
        types = sample[0].entity_types[0] if sample[0].entity_types  else 'things'
        say += ' Now I know %s %s that %s %s, like %s and %s' % (len(overlaps), types,
                                                                 utterance.triple.predicate_name,
                                                                 utterance.triple.complement_name,
                                                                 sample[0].entity_name, sample[1].entity_name)

    return say


def phrase_trust(trust):
    if trust == 1:
        say = random.choice(TRUST)
    else:
        say = random.choice(NO_TRUST)

    return say


def phrase_thoughts(update, entity_only=False, proactive=True, persist=False):
    """
    Phrase a random thought
    Parameters
    ----------
    update
    entity_only
    proactive
    persist

    Returns
    -------

    """
    if entity_only:
        options = ['cardinality_conflicts', 'negation_conflicts', 'statement_novelty', 'entity_novelty']
    else:
        options = ['cardinality_conflicts', 'entity_novelty']

    if proactive:
        options.extend(['subject_gaps', 'complement_gaps', 'overlaps'])

    # Casefold and select approach randomly
    utterance = update['statement']
    if utterance.triple is None:
        return None

    utterance.casefold(format='natural')
    thoughts = update['thoughts']
    thoughts.casefold(format='natural')
    approach = random.choice(options)
    say = None

    if approach == 'cardinality_conflicts':
        say = _phrase_cardinality_conflicts(thoughts.complement_conflicts(), utterance)

    elif approach == 'negation_conflicts':
        say = _phrase_negation_conflicts(thoughts.negation_conflicts(), utterance)

    elif approach == 'statement_novelty':
        say = _phrase_statement_novelty(thoughts.statement_novelties(), utterance)

    elif approach == 'entity_novelty':
        say = _phrase_type_novelty(thoughts.entity_novelty(), utterance)

    elif approach == 'subject_gaps':
        say = _phrase_subject_gaps(thoughts.subject_gaps(), utterance)

    elif approach == 'complement_gaps':
        say = _phrase_complement_gaps(thoughts.complement_gaps(), utterance)

    elif approach == 'overlaps':
        say = _phrase_overlaps(thoughts.overlaps(), utterance)

    if persist and say is None:
        say = phrase_thoughts(update, proactive, persist)

    return say

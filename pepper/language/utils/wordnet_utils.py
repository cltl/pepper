#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 09:37:31 2019

@author: andrasaponyi
"""

from nltk.corpus import wordnet as wn


# Synset types: n, v, a, r (adverb), s (adjective satellite).
def get_synsets(word, tag):
    """ Look up and return all possible synset of an input word. """

    if tag.startswith('N'):
        POS = "n"
    elif tag.startswith('V'):
        POS = "v"
    elif "J" in tag:
        POS = "a"
    elif "RB" in tag:
        POS = "r"
    else:
        POS = None

    synsets = []
    s_sets = wn.synsets(word)
    for s_set in s_sets:
        if s_set.pos() == POS:
            synsets.append(s_set)
        elif s_set.pos() == "s" and POS == "a":
            synsets.append(s_set)

    return synsets


# Get a collection of synonymous words.
def get_lemmas(synset):
    """ Look up and return all lemmas of a given synset. """

    lemmas = synset.lemma_names()

    return lemmas


# Can be used in disambiguation, e.g. Leolani can ask "Do you mean [definition]?".
def get_definition(synset):
    """ Look up and return the definition of a synset. """

    definition = synset.definition()

    return definition


# Useful for finding out what kind of thing is being talked about.
# Lexnames include: noun.animal, noun.person, noun.food, verb.emotion, verb.possession, etc.
def get_lexname(synset):
    """ Look up and return the lexname of a given synset. """

    lexname = synset.lexname()

    return lexname


# Can be used in disambiguation, e.g. Leolani can ask "Do you mean a type of [hypernym]?".
def get_hypernyms(synset):
    """ Look up and return higher-levels concepts for a given synset. """

    hypernyms = synset.hypernyms()
    hypernyms = sorted(lemma.name() for synset in hypernyms for lemma in synset.lemmas())

    return hypernyms


def get_root(synset):
    """ Look up and return the most general hypernym of a given sysnet. """

    root = synset.root_hypernyms()
    root = sorted(lemma.name() for synset in root for lemma in synset.lemmas())

    return root


def get_hyponyms(synset):
    """ Look up and return more specific synsets for a given synset. """

    hyponyms = synset.hyponyms()
    hyponyms = sorted(lemma.name() for synset in hyponyms for lemma in synset.lemmas())

    return hyponyms


def get_parts(synset):
    """ Look up and return the part meronyms of a given synset. """

    parts = synset.part_meronyms()
    parts = sorted(lemma.name() for synset in parts for lemma in synset.lemmas())

    return parts


def get_substance(synset):
    """ Look up and return the substance meronyms of a given synset. """

    substance = synset.substance_meronyms()
    substance = sorted(lemma.name() for synset in substance for lemma in synset.lemmas())

    return substance


def get_holonyms(synset):
    """ Look up and return the holonyms of a given synset. """

    holonyms = synset.member_holonyms()
    holonyms = sorted(lemma.name() for synset in holonyms for lemma in synset.lemmas())

    return holonyms


def get_entailments(synset):
    """ Look up and return the entailments for a given verbal synset. """

    entailments = synset.entailments()
    entailments = sorted(lemma.name() for synset in entailments for lemma in synset.lemmas())

    return entailments


def get_antonyms(synset):
    """ Look up and return the antonyms of lemmas in a given synset. """

    antonyms_all = []
    for lemma in synset.lemmas():
        antonyms = lemma.antonyms()
        for ant in antonyms:
            antonyms_all.append(ant.name())

    return antonyms_all

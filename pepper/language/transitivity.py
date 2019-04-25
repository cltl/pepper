#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 11:28:43 2019

@author: andrasaponyi
"""

from nltk.corpus import verbnet as vn
from nltk.corpus import wordnet as wn

def get_transitivity(verb):
    """ 
    Take a verb lemma as input.
    Return transitivity score and VerbNet (VN) frames if available. 
    
    The returned tuple is constructed in the following way:
        -the first element is the transitivity score, where:
            -1 equals transitive
            -0 equals intransitive (or at least according to VN)
        -the second element is a list of tuples, each of which consists of:
            -first, the VN class_id of a given meaning of a verb
            -second, the corresponding frame itself
            
    Regardless of the length of the transitive frames list, 
    the transitivty score remains the same.
    """
    
    class_ids = vn.classids(verb)

    print(class_ids)

    # Define a list containing frames with transitive meanings of the given verb.
    trans_frames = []
    for class_id in class_ids:
        frames = vn.frames(class_id)
        for frame in frames:
            print (frame["description"]["primary"])
            #print(frame['description']['secondary'])
            if frame["description"]["primary"] == "NP V NP":
                entry = class_id, frame
                trans_frames.append(entry)
#            elif "NP V NP" in frame["description"]["primary"]:
#                entry = class_id, frame
#                trans_frames.append(entry)
#            elif "Transitive" in frame["description"]["secondary"]:
#                entry = class_id, frame
#                trans_frames.append(entry)

    # If the trans_score is equal to one, the verb has a transitive meaning.
    if len(trans_frames) != 0:
        trans_score = 1
    
    else:
        trans_score = 0
        
    return trans_score, trans_frames
    
def get_synonyms(verb):
    """ Return the synonyms of the most frequent sense of a verb. """
    
    synsets = wn.synsets(verb)
    
    for synset in synsets:
        if ".v." in str(synset):
            most_frequent = synset
            synonyms = most_frequent.lemma_names()
            
            return synonyms
        
def check_synonyms(verb):
    """
    Return the transitivity of a verb's synonyms. 
    To be called if the initial transitivity score is 0, but there is
    reason to believe that the verb is indeed transitive.
    I am still working on a method to determine how this decision can be made.
    """
    
    synonyms = get_synonyms(verb)
    if not synonyms == None:
        for synonym in synonyms:
                if synonym != verb:
                    transitivity = get_transitivity(synonym)
            
                    return transitivity
    # Otherwise the function will return a TypeError. 
    else:
        return None
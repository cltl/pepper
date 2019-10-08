# coding=utf-8

from pepper.brain.fame_aware import FameAwareMemory

if __name__ == "__main__":

    # Create brain connection
    brain = FameAwareMemory()

    people = ["Máxima of the Netherlands", "Brexit"]

    for elem in people:
        x = brain.lookup_person_wikidata(elem)


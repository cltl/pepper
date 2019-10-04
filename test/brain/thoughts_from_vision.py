from pepper.brain.long_term_memory import LongTermMemory
from pepper.brain.utils.base_cases import visuals

from pepper.language.generation.thoughts_phrasing import phrase_thoughts

if __name__ == "__main__":

    # Create brain connection
    brain = LongTermMemory()

    flat_list = [item for detection in visuals for item in detection]
    experience = set(flat_list)

    for elem in experience:
        x = brain.get_thoughts_on_entity(elem, reason_types=True)

        print('\t\t\tFINAL SAY: ' + phrase_thoughts(x, proactive=True, persist=True))

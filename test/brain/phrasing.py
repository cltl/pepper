from pepper.language.generation.thoughts_phrasing import phrase_thoughts
from pepper.brain import LongTermMemory

from test.brain.utils import transform_capsule, bl, capsule_likes, capsule_is_from, capsule_is_from_2, \
    capsule_is_from_3, capsule_knows

from random import choice

if __name__ == "__main__":

    # Create brain connection
    brain = LongTermMemory(clear_all=True)

    capsules = [capsule_likes, capsule_is_from, capsule_is_from_2, capsule_is_from_3, capsule_knows]

    for capsule in capsules:
        say = ''
        em = choice(bl)
        np = choice(bl)
        p = choice(bl)
        capsule = transform_capsule(capsule, empty=em, no_people=np, place=p)
        x = brain.update(capsule, reason_types=True)

        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))
        print(phrase_thoughts(x, True, True))

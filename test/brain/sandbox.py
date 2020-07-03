from pepper.language.generation.thoughts_phrasing import phrase_thoughts
from pepper.brain import LongTermMemory

from test.brain.utils import transform_capsule, places, binary_values, capsule_is_from, capsule_is_from_2, \
    capsule_is_from_3, capsule_knows

from random import choice

if __name__ == "__main__":

    # Create brain connection
    brain = LongTermMemory(clear_all=True)

    capsules = [capsule_is_from, capsule_is_from_2, capsule_is_from_3, capsule_knows,
                capsule_is_from, capsule_is_from_2, capsule_is_from_3, capsule_knows]

    for capsule in capsules:
        say = ''
        em = choice(binary_values)
        np = choice(binary_values)
        p = choice(binary_values)
        capsule = transform_capsule(capsule, empty=em, no_people=np, place=p)
        x = brain.update(capsule, reason_types=True)

        if capsule.context.location.label == capsule.context.location.UNKNOWN:
            y = brain.reason_location(capsule.context)
            if y is None:
                z = choice(places)
                brain.set_location_label(z)
                capsule.context.location._label = z
                say += 'Having a talk at what I will call %s' % capsule.context.location.label
            else:
                brain.set_location_label(y)
                capsule.context.location._label = y
                say += 'Having a talk at what I figure out is %s' % capsule.context.location.label

        else:
            say += 'Having a talk at %s' % capsule.context.location.label
        print(say)

        for x in range(10):
            print(phrase_thoughts(x, True, True))

    # for x in range(10):
    #     say = ''
    #     emn = choice(bl)
    #     npn = choice(bl)
    #     context = fake_context(empty=emn, no_people=npn)
    #     say += 'Compared with context b: %s,%s\n' % (emn, npn)
    #
    #     y = brain.reason_location(context)
    #     if y is None:
    #         z = choice(places)
    #         # brain.set_location_label(z)
    #         context.location._label = z
    #         say += 'I did not know where I was, but I will call it %s' % context.location.label
    #     else:
    #         # brain.set_location_label(y)
    #         context.location._label = y
    #         say += 'I assume I am at %s' % context.location.label
    #
    #     print(say)

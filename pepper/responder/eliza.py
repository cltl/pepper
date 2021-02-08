import re
import random
import pepper.responder.eliza_niqee as niqee
import pepper.responder.eliza_language as lang

NAME="Eliza"

def reflect(fragment):
    tokens = fragment.lower().split()
    for i, token in enumerate(tokens):
        if token in lang.REFLECTIONS:
            tokens[i] = lang.REFLECTIONS[token]
    return ' '.join(tokens)


def analyzeniqee(statement):
    for pattern, responses in niqee.PSYCHOBABBLE:
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
            response = random.choice(responses)
            return response.format(*[reflect(g) for g in match.groups()])

def isee(statement):
    for pattern, responses in niqee.ISEE:
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
            response = random.choice(responses)
            return response.format(*[reflect(g) for g in match.groups()])

def analyze(statement):
    for pattern, responses in lang.PSYCHOBABBLE:
        match = re.match(pattern, statement.rstrip(".!"))
        if match:
            response = random.choice(responses)
            return response.format(*[reflect(g) for g in match.groups()])


def talk_to_me():
    print("Hello. I am "+NAME+". I am your personal therapist and your best friend. How are you feeling today?")

    while True:
        statement = input("> ")
        print(analyze(statement))

        # if statement == "quit":
        #     break


if __name__ == "__main__":
    talk_to_me()
from pepper.conversation.BDI import BDI

import time


def main(_):
    conversation_model = BDI()

    # General
    conversation_model.current_beliefs_environment['session_start'] = time.strftime('%Y-%m-%d %H:%M:%S')

    # Boolean flags
    conversation_model.current_beliefs_environment['person_in_frame'] = False
    conversation_model.current_beliefs_environment['person_known'] = False
    conversation_model.current_beliefs_environment['person_talking'] = False

    conversation_model.current_beliefs_internal['understood'] = False

    # Counters
    conversation_model.current_beliefs_environment['number_people_seen'] = 0

    conversation_model.current_desire = 0
    conversation_model.current_intention = 0

    # Choose action
    intention, intention_label = conversation_model.next_intention()

    print('Switched to %s' % intention_label)


if __name__ == "__main__":
    main(None)

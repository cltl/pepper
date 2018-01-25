from pepper.apps.cltl_meetgreet import brain
import utils

import twitter
import yaml
import os
from random import choice
from time import sleep, strftime


HASHTAG = 'askleolani'

GREETINGS = [
    "Hi", "Hello", "Good afternoon", "Hey there", "Hey",
]

# Authenticate to Leolani Twitter Account
with open(os.path.join(utils.PATH, 'twitter_auth.yaml')) as yaml_file:
    auth = yaml.load(yaml_file)

api = twitter.Api(
    consumer_key=auth['consumer_key'],
    consumer_secret=auth['consumer_secret'],
    access_token_key=auth['access_token_key'],
    access_token_secret=auth['access_token_secret']
)

REPLIED = set(reply.in_reply_to_status_id for reply in api.GetReplies())

while True:
    print "\rChecking for Questions ({})".format(strftime("%H:%M:%S")),
    for question in api.GetSearch(raw_query='q=%23{}'.format(HASHTAG)):
        try:
            if question.id not in REPLIED:
                answer = u"{} {}, {}".format(choice(GREETINGS), question.user.name, brain(question.text))
                print(u"\r{:14s}: {} -> {}".format(question.user.name, question.text, answer))
                api.PostUpdate(answer, in_reply_to_status_id=question.id, auto_populate_reply_metadata=True)
                REPLIED.add(question.id)
        except Exception as e:
            print("\rCouldn't Answer")
            print(e)
            REPLIED.add(question.id)
    sleep(10)
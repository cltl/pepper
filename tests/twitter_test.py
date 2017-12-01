from pepper.knowledge.wolfram import Wolfram
import utils

import twitter
import yaml
import os
from random import seed, choice
from time import sleep

GREETINGS = [
    "Hi", "Hello", "Good afternoon", "Yo", "Hey there", "Hey", "Thank you for your question"
]

with open(os.path.join(utils.PATH, 'twitter_auth.yaml')) as yaml_file:
    auth = yaml.load(yaml_file)

api = twitter.Api(
    consumer_key=auth['consumer_key'],
    consumer_secret=auth['consumer_secret'],
    access_token_key=auth['access_token_key'],
    access_token_secret=auth['access_token_secret']
)

REPLIED = set()

for reply in api.GetReplies():
    REPLIED.add(reply.in_reply_to_status_id)

for question in api.GetSearch(raw_query='q=%23askleolani'):
    if question.id not in REPLIED:
        print("{:14s} {}".format(question.user.name, question.text))
        seed(sum(ord(char) for char in question.user.screen_name))
        answer = "{} {}, {}".format(choice(GREETINGS), question.user.name, Wolfram().query(question.text))
        api.PostUpdate(answer, in_reply_to_status_id=question.id, auto_populate_reply_metadata=True)
        REPLIED.add(question.id)
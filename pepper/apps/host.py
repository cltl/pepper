import random
from pepper.app import App


class Host(App):

    SECONDS_BETWEEN_ATTENTIONS = 60
    SECONDS_BETWEEN_GREETINGS = 60
    SECONDS_LISTENING_FOR_QUESTION = 30

    ASK_FOR_QUESTION = [
            "I'm listening",
            "Shoot me a question",
            "What would you like to know?",
            "What's your question?",
            "I am ready for your question",
            "Ask me",
            "Let's hear your question"
        ]


    def load_speakers():
        file = 'speakers.txt'
        f = open(file, "r")
        raw = f.read()
        info = raw.splitlines()
        structured = []
        for line in info:
            speaker = {}
            raw = line.split(',')
            name = raw[0].split(' ')
            speaker['name'] = name[0].strip()
            if len(name) is 3:
                speaker['lastname'] = name[1].strip() + ' ' + name[2].strip()
            else:
                speaker['lastname'] = name[1].strip()
            key = 'occupation'
            for elements in raw[1:]:
                speaker[key] = elements.strip()
                if ':' in speaker[key]:
                    if '(' in speaker[key]:
                        speaker[key]=speaker[key].split('(')[0].strip()
                    speaker['company'] = speaker[key].split(':')[0].strip()
                    speaker['title'] = speaker[key].split(':')[1].strip()
                    speaker.pop(key)
                key = 'occupation2'
            structured.append(speaker)
        return structured


greet = 'Hi, I am LeoLani and will be your host today! It is so nice to see all of you here. We will hear many interesting speakers. ' \
        'Since we do not have much time, we should start right away! Please, pardon my Dutch... '

invite = ['And now ','And now let us welcome ', 'Our next speaker is ', 'And now, please welcome ',
          'Let us hear from ', 'Our next pitch is from ', 'Please welcome ', 'The next speaker is ', 'The next presentation is from ']

thank = ['', 'Wow! ', 'How interesting! ']


def main():
    speakers = Host.load_speakers()
    i = 0
    #connect 192.168.1.103
    print(greet)
    for speaker in speakers:
        welcome = ''
        goodbye=''
        fullname = speaker['name']+' '+speaker['lastname']
        if 'company' in speaker:
            job = speaker['title']+' in '+speaker['company']
        else:
            job=' from ' + speaker['occupation']

        welcome = random.choice(invite)  +fullname +', '+ job + '!'
        goodbye = random.choice(thank)+'Thank you, ' + speaker['name']+'!'
        if i == 0:
            welcome='Our first speaker is '+ fullname+', '  +job+'!'
        if i == len(speakers)-1:
            welcome='And the last speaker for tonight is '+fullname +', ' +job+'!'
            goodbye='This was the last presentation for today! I hope you had as much fun as I did... Do not forget to stay for drinks!'
        i += 1
        print(welcome)
        #wait for signal
        print(goodbye)


if __name__ == "__main__":
    Host(["192.168.1.102", 9559]).run()
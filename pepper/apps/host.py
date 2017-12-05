import random
from pepper.app import App


class Host(App):

    def __init__(self, address):
        super(Host, self).__init__(address)
        self.speech = self.session.service("ALAnimatedSpeech")
        speakers = self.load_speakers()
        print(greet)
        self.speech.say(greet)
        i=0
        for speaker in speakers:
            fullname = ','+ speaker['name'] + ' ' + speaker['lastname']
            if 'company' in speaker:
                job = speaker['title'] + ' in ' + speaker['company']
            else:
                job = speaker['occupation']
            welcome=''
            if i==7:
                welcome='I hope everyone enjoyed their break, I had the opportunity to cool down a little bit...'
            welcome = welcome+ random.choice(invite) + fullname + ',... ' + job + '!'
            goodbye = random.choice(thank) + 'Thank you, ' + speaker['name'] + '!...'
            if i == 0:
                welcome = 'Our first speaker is ' + fullname + ',... ' + job + '!'
            if i == len(speakers) - 1:
                welcome = 'And the last speaker for today is ' + fullname + ',... ' + job + '!'
                goodbye += 'This was the last company pitch! I hope you had as much fun as I did... I wish I was a computational linguist!' \
                           '... Now we will hear the remaining student pitches!' \
                           '... Do not forget to stay for drinks and Q and A with me afterwards! ...Also, you can ask me anything - ' \
                           'on my twitter account! Hashtag Ask Leo-lani'
            if i==6:
                goodbye+='And now, we have the opportunity to meet the newest computational linguists from the VU,' \
                         ' please welcome our Master students from Human Language Technology and Forensic Linguistics!...' \
                         ' After their pitches, ' \
                         'we have a coffee break and then we continue with the program at half past three.'

            i += 1
            if speaker['name']=='Mart-aighn':
                welcome+='Welcome back to the VU, Mart-aighn!'
            print(welcome)
            self.speech.say(welcome)
            raw_input('Press enter for next speaker...')
            print(goodbye)
            self.speech.say(goodbye)
            if i==7:
                raw_input('Press enter when the break is over...')

    def load_speakers(self):
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



greet = '\\rspd=90\\Thank you for the introduction Piek. ... I am LeoLani and will be your host today! It is so nice to see all of you here. We will hear many interesting speakers. ' \
        'Since we do not have much time, we should start right away! Please, pardon my Dutch... '

invite = ['And now ','And now let us welcome ', 'Our next speaker is ', 'And now, please welcome ',
          'Let us hear from ', 'Our next pitch is from ', 'Please welcome ', 'The next speaker is ', 'The next presentation is from ']

thank = ['Awesome!', 'Wow! ', 'How interesting! ', 'A really nice presentation, ', 'Super!']

if __name__ == "__main__":
    Host(["192.168.1.103", 9559]).run()
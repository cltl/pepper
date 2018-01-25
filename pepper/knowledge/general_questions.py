LeoLani = 	{'name': 'Leo Lani', 'origin': 'France', 'age':'a few months', 'weight':'28', 'height':'120', 
			'meaning':'Voice of heaven', 'gender': 'female', 'feeling': 'good'}
			

	
def answer_trigger(key):

	Properties = {'name': 'Leo Lani', 'weight':'28', 'height':'120', 'gender': 'female', 
		'work':'understanding humans', 'age': 'just a few months'}
	
	Favorites =	{'book': 'the Hobbit', 'animal':'an elephant', 'writer':'Isaak Asimov', 'movie':'WALL-E',
			'food':'electricity', 'colour':'blue', 'song':'Ode to joy', 'sport':'kung-fu ^start(animations/Stand/Waiting/MysticalPower_1)',
                    'instrument':'human voice','drink':'streams of bits', 'weather':'sunny'}
	
	Abilities = {'dance':'I love dance!', 
			'joke': 'What does Batman say to Robin before they get in the Batmobile? ... Robin, get in the Batmobile',
			'answer': 'But I do not know everything'}

	answer=''
	if key in Properties.keys():
		answer = 'My ' + key + ' is ' + Properties.get(key)
	if key in Favorites.keys():
		answer = 'My favorite ' + key + ' is ' + Favorites.get(key)
	if key in Abilities.keys():
		answer = 'Sure I can! ' + Abilities.get(key)
	return answer
	

def general_questions(line):
    line.strip()
    words = line.split(' ')
    if 'your' in words or 'yours' in words or 'you' in words:
        if 'made' in words or 'created' in words:
            return('I was made by my programmers')
        if 'how' in words:
            if 'old' in words:
                return('I am just a few months old')
            else:
                return('I am great, thank you for asking!')
        if 'love' in words or 'hate' in words or 'think' in words:
            return('I still need time to learn more about the world, ask me in a couple of years')
        if 'where' in words and 'from' in words:
            return('I am from France and Japan! But I have been to Hawaii')
        if 'mean' in words:
            return("My name 'Leo Lani', means \\rspd=85\\ \\vct=70\\ 'Voice of an Angel!'")
        if 'boy' in words or 'girl' in words or 'male' in words or 'female' in words:
            answer_trigger('gender')
        for word in words:
            answer = answer_trigger(word)
            if answer: return answer


		
			







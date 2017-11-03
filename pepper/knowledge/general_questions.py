LeoLani = 	{'name': 'Leo Lani', 'origin': 'France', 'age':'a few months', 'weight':'28', 'height':'120', 
			'meaning':'Voice of heaven', 'gender': 'female', 'feeling': 'good'}
			

	
def answer_trigger(key):

	Properties = {'name': 'Leo Lani', 'weight':'28', 'height':'120', 'gender': 'female', 
		'work':'understanding humans', 'age': 'just a few months'}
	Properties_questions = ['What is your '+key]
	
	Favorites =	{'book': 'the Hobbit', 'animal':'elefant', 'writer':'Isaak Asimov', 'movie':'WALL-E', 
			'food':'electricity', 'colour':'blue', 'song':'Ode to joy'}
	Favorites_questions = ['Do you have a favorite '+key, 'What is your favorite '+key]
	
	Abilities = {'dance':'I love dance!', 
			'joke': 'What does Batman say to Robin before they get in the Batmobile? ... Robin, get in the Batmobile',
			'answer': 'But I do not know everything'}
	Abilities_questions = ['Can you '+ key]

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
    if 'your' in words or 'yours' in words or 'you':
        if 'how' in words:
            return('I am great, thank you for asking!')
        if 'love' in words or 'hate' in words or 'think' in words:
            return('I still need time to learn more about the world, ask me in a couple of years')
        if 'where' in words and 'from' in words:
            return('I am from France ')
        for word in words:
            answer = answer_trigger(word)
            if answer: return answer


		
			







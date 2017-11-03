LeoLani = 	{'name': 'Leo Lani', 'origin': 'France', 'age':'a few months', 'weight':'28', 'height':'120', 
			'meaning':'Voice of heaven', 'gender': 'female', 'feeling': 'good'}
			
def answer_question(line):

	name_questions = ['What is your name?', 'Do you have a name', 'How are you called']
	name_answers = ['My name is '+LeoLani['name'], 'You can call me '+LeoLani['name']]

	origin_questions = ['Where are you from', 'Where do you come from']
	origin_answers = ['I am from '+LeoLani['origin'], 'I was made in '+LeoLani['origin']]

	age_questions = ['What is your age', 'How old are you']
	age_answers = ['I am very young, only '+LeoLani['age'], 'I am '+LeoLani['age']+' old']

	meaning_questions = ['What does your name mean', 'Does your name mean anything', 'What does '+LeoLani['name']+' mean']
	meaning_answers = [LeoLani['name']+' means '+LeoLani['meaning']+' in Hawaiian', 'My name means '+LeoLani['meaning']+' in Hawaiian']

	height_questions = ['What is your height', 'How high are you']
	height_answers = ['My height is '+LeoLani['height'], 'I am '+LeoLani['height']+' centimeters high']

	weight_questions = ['What is your weight', 'How much do you weigh']
	weight_answers = ['My weight is '+LeoLani['weight']+' kilograms', 'I am '+LeoLani['weight']+' kilograms heavy']

	gender_questions = ['What is your gender', 'Do you have a gender', 'Are you a boy or girl', 'Are you man or woman']
	gender_answers = ['I am '+LeoLani['gender'], 'My gender is '+LeoLani['gender']]

	feeling_questions = ['How are you', 'How is it going', 'What is up', 'Do you like it here']
	feeling_answers = ['Thank you for asking, I feel '+LeoLani['feeling'], 'It is all '+LeoLani['feeling'] +' and how are you']
	
	answer=None
	print(line)
	if line in name_questions:
		answer = name_answers[1]
	if line in origin_questions:
		answer = origin_answers[1]
	if line in meaning_questions:
		answer = meaning_answers[1]
	if line in age_questions:
		answer = age_answers[1]
	if line in gender_questions:
		answer = gender_answers[0]
	if line in feeling_questions:
		answer = feeling_answers[1]
	return answer
		
		
	
	
def answer_trigger(key):

	Properties = {'name': 'Leo Lani', 'weight':'28', 'height':'120', 'gender': 'female', 
		'work':'understanding humans'}
	Properties_questions = ['What is your '+key]
	#Properties_answers = ['My ' + key + ' is ' + Properties.get(key)]
	
	Favorites =	{'book': 'the Hobbit', 'animal':'elefant', 'writer':'Isaak Asimov', 'movie':'WALL-E', 
			'food':'electricity', 'color':'blue', 'song':'Ode to joy'}
	Favorites_questions = ['Do you have a favorite '+key, 'What is your favorite '+key]
	#Favorites_answers = ['My favorite ' + key + ' is ' + Favorite.values[key], 
	#					'I enjoy '+Favorites.values[key]+' the most!']
	
	
	Abilities = {'dance':'I love dance!', 
			'tell a joke': 'What does Batman say to Robin before they get in the Batmobile Robin, get in the Batmobile', 
			'answer a question': 'But I do not know everything'}
	Abilities_questions = ['Can you '+ key]
	#Abilities_answers = ['Sure I can!' + Abilities.values[key]]
	#print(key)
	answer=''
	if key in Properties.keys():
		answer = 'My ' + key + ' is ' + Properties.get(key)
	if key in Favorites.keys():
		answer = 'My favorite ' + key + ' is ' + Favorites.get(key)
	if key in Abilities.keys():
		answer = 'Sure I can! ' + Abilities.get(key)
	return(answer)
	

# ''' do you drink coffee / do you like pandas / what do you study/ where do you work '''
# from nltk import word_tokenize
# import re
#
# with open("/Users/lenka/Desktop/input.txt","r") as file:
#     input = file.readlines()
# print(input)
# line = re.sub("[^a-zA-Z]",  # Search for all non-letters
#                           " ",          # Replace all non-letters with spaces
#                           str(input))
# for line in input:
# 	line.strip()
# 	answer = answer_question(line)
# 	if answer is not None:
# 		print('answered full question '+answer)
# 	if answer is None:
#
#
# 		words = word_tokenize(line)
#
# 		for word in words:
# 			answer = answer_trigger(word)
# 			print(answer)
			







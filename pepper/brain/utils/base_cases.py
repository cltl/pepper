from datetime import date

statements = [
    {  # lenka is from Serbia
        "subject": {
            "label": "lenka",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "serbia",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 1,
        "position": "0-27",
        "date": date.today()
    },
    {  # bram is from the netherlands
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "netherlands",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 2,
        "position": "0-27",
        "date": date.today()
    },
    {  # selene is from mexico
        "subject": {
            "label": "selene",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "mexico",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 3,
        "position": "0-27",
        "date": date.today()
    },
    {  # piek is from the netherlands
        "subject": {
            "label": "piek",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "netherlands",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 4,
        "position": "0-27",
        "date": date.today()
    },
    {  # selene K is from the netherlands
        "subject": {
            "label": "selene_k",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "netherlands",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 5,
        "position": "0-27",
        "date": date.today()
    },
    {  # bram likes goulash
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "goulash",
            "type": "dish"
        },
        "author": "selene",
        "chat": 1,
        "turn": 6,
        "position": "0-25",
        "date": date.today()
    },
    {  # bram likes The Big Lebowski
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "the_big_lebowski",
            "type": "movie"
        },
        "author": "selene",
        "chat": 1,
        "turn": 7,
        "position": "0-25",
        "date": date.today()
    },
    {  # bram likes baseball
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "baseball",
            "type": "sport"
        },
        "author": "selene",
        "chat": 1,
        "turn": 8,
        "position": "0-25",
        "date": date.today()
    },
    {  # bram likes romantic movies
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "romantic_movies",
            "type": "film_genre"
        },
        "author": "selene",
        "chat": 1,
        "turn": 9,
        "position": "0-25",
        "date": date.today()
    },
    {  # lenka likes ice cream
        "subject": {
            "label": "lenka",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "ice_cream",
            "type": "dish"
        },
        "author": "selene",
        "chat": 1,
        "turn": 10,
        "position": "0-25",
        "date": date.today()
    },
    {  # lenka likes Harry Potter
        "subject": {
            "label": "lenka",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "harry_potter",
            "type": "movie"
        },
        "author": "selene",
        "chat": 1,
        "turn": 11,
        "position": "0-25",
        "date": date.today()
    },
    {  # lenka likes acrobatics
        "subject": {
            "label": "lenka",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "acrobatics",
            "type": "sport"
        },
        "author": "selene",
        "chat": 1,
        "turn": 12,
        "position": "0-25",
        "date": date.today()
    },
    {  # lenka likes action movies
        "subject": {
            "label": "lenka",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "action_movies",
            "type": "film_genre"
        },
        "author": "selene",
        "chat": 1,
        "turn": 13,
        "position": "0-25",
        "date": date.today()
    },
    {  # piek likes balkenbrij
        "subject": {
            "label": "piek",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "balkenbrij",
            "type": "dish"
        },
        "author": "selene",
        "chat": 1,
        "turn": 14,
        "position": "0-25",
        "date": date.today()
    },
    {  # piek likes 2001 A Space Odyssey
        "subject": {
            "label": "piek",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "2001_a_space_odyssey",
            "type": "movie"
        },
        "author": "selene",
        "chat": 1,
        "turn": 15,
        "position": "0-25",
        "date": date.today()
    },
    {  # piek likes soccer
        "subject": {
            "label": "piek",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "soccer",
            "type": "sport"
        },
        "author": "selene",
        "chat": 1,
        "turn": 16,
        "position": "0-25",
        "date": date.today()
    },
    {  # piek likes horror movies
        "subject": {
            "label": "piek",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "horror_movies",
            "type": "film_genre"
        },
        "author": "selene",
        "chat": 1,
        "turn": 17,
        "position": "0-25",
        "date": date.today()
    },
    {  # selene likes tacos
        "subject": {
            "label": "selene",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "tacos",
            "type": "dish"
        },
        "author": "selene",
        "chat": 1,
        "turn": 18,
        "position": "0-25",
        "date": date.today()
    },
    {  # selene likes Coco
        "subject": {
            "label": "selene",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "coco",
            "type": "movie"
        },
        "author": "selene",
        "chat": 1,
        "turn": 19,
        "position": "0-25",
        "date": date.today()
    },
    {  # selene likes soccer
        "subject": {
            "label": "selene",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "soccer",
            "type": "sport"
        },
        "author": "selene",
        "chat": 1,
        "turn": 20,
        "position": "0-25",
        "date": date.today()
    },
    {  # selene likes animated movies
        "subject": {
            "label": "selene",
            "type": "person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "animated_movies",
            "type": "film_genre"
        },
        "author": "selene",
        "chat": 1,
        "turn": 21,
        "position": "0-25",
        "date": date.today()
    },
    {  # bram knows lenka
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "knows"
        },
        "object": {
            "label": "lenka",
            "type": "person"
        },
        "author": "selene",
        "chat": 1,
        "turn": 22,
        "position": "0-16",
        "date": date.today()
    },
    {  # Leolani is from France
        "subject": {
            "label": "leolani",
            "type": "robot"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "france",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 23,
        "position": "0-27",
        "date": date.today()
    },
    {  # Leolani is from Japan
        "subject": {
            "label": "leolani",
            "type": "robot"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "japan",
            "type": "location"
        },
        "author": "selene",
        "chat": 1,
        "turn": 24,
        "position": "0-27",
        "date": date.today()
    },
    {  # lenka mother is ljubica (lenka)
        u'predicate': {u'type': u'mother_is'},
        u'chat': u'',
        u'author': u'lenka',
        u'object': {u'type': u'', u'id': u'', u'label': u'ljubica'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'lenka'}
    },
    {  # bram likes action movies (bram)
        u'predicate': {u'type': u'likes'},
        u'chat': u'',
        u'author': u'bram',
        u'object': {u'type': u'', u'id': u'', u'label': u'action_movies'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # bram likes romantic movies (selene)
        u'predicate': {u'type': u'likes'},
        u'chat': u'',
        u'author': u'selene',
        u'object': {u'type': u'', u'id': u'', u'label': u'romantic_movies'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # bram is_from Italy (selene)
        u'predicate': {u'type': u'is_from'},
        u'chat': u'',
        u'author': u'selene',
        u'object': {u'type': u'location', u'id': u'', u'label': u'italy'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # lenka favorite food-is cake (lenka)
        u'predicate': {u'type': u'favorite'},
        u'chat': u'',
        u'author': u'lenka',
        u'object': {u'type': u'', u'id': u'', u'label': u'cake'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'lenka'}
    }
]

questions = [
    {
        u'predicate': {u'type': 'is_from'},
        u'chat': 0,
        u'author': u'jo',
        u'object': {u'type': u'', u'id': u'', u'label': ''},
        u'turn': 7, u'utterance_type': 'question',
        u'date': '',
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}},
    {  # Who is from the Serbia? -> lenka, selene
        "subject": {
            "label": "",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "serbia",
            "type": "location"
        }
    },
    {  # Where is lenka from? -> Serbia, selene
        "subject": {
            "label": "lenka",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "",
            "type": "location"
        }
    },
    {  # Does selene know piek? -> (yes) selene
        "subject": {
            "label": "selene",
            "type": "person"
        },
        "predicate": {
            "type": "knows"
        },
        "object": {
            "label": "piek",
            "type": "person"
        }
    },
    {  # Is bram from the netherlands? -> (idk) empty
        "subject": {
            "label": "bram",
            "type": "person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "netherlands",
            "type": "location"
        }
    },
    {  # bram knows Beyonce
        u'predicate':
            {u'type': u'knows'},
        u'chat': u'',
        u'author': u'person',
        u'object':
            {u'type': u'', u'id': u'', u'label': u'beyonce'},
        u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # Leolani knows bram
        u'predicate': {u'type': u'knows'}, u'chat': u'', u'author': u'bram',
        u'object': {u'type': u'person', u'id': u'', u'label': u'bram'}, u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'leolani'}
    },
    {  # selene knows piek
        u'predicate': {u'type': u'knows'}, u'chat': u'', u'author': u'person',
        u'object': {u'type': u'person', u'id': u'', u'label': u'piek'}, u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'selene'}
    },
    {  # Where is Leolani from?
        u'predicate': {u'type': u'is_from'}, u'chat': u'', u'author': u'person',
        u'object': {u'type': u'', u'id': u'', u'label': u''}, u'turn': u'', u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'leolani'}
    },
    {  # Who is from italy
        u'predicate': {u'type': u'is_from'}, u'chat': u'', u'author': u'jill',
        u'object': {u'type': u'', u'id': u'', u'label': u'italy'}, u'turn': u'', u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u''}
    },
    {  # what does piek like (jo)
        u'predicate': {u'type': u'likes'},
        u'chat': u'',
        u'author': u'jo',
        u'object': {u'type': u'', u'id': u'', u'label': u''},
        u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'piek'}
    }
]

experiences = [
    {  # Leolani saw an apple
        "subject": {
            "label": "",
            "type": ""
        },
        "predicate": {
            "type": ""
        },
        "object": {
            "label": "apple",
            "type": "fruit"
        },
        "author": "front_camera",
        "chat": None,
        "turn": None,
        "position": "0-15-0-15",
        "date": date.today()
    }
]

visuals = [
['tv', "carpenter's kit", 'tool kit'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['laptop', 'laptop', 'laptop computer'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'laptop', 'laptop computer'],
['laptop', 'laptop', 'laptop computer'],
['laptop', 'laptop', 'laptop computer'],
['laptop', 'laptop', 'laptop computer'],
['laptop', 'laptop', 'laptop computer'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'printer'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['laptop', 'notebook', 'notebook computer'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['tv', 'espresso maker'],
['tv', 'espresso maker'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['tv', 'espresso maker'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['chair', 'desk'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', "potter's wheel"],
['potted plant', 'pot', 'flowerpot'],
['potted plant', "potter's wheel"],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['tv', 'espresso maker'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', "potter's wheel"],
['potted plant', 'pot', 'flowerpot'],
['tv', 'pay-phone', 'pay-station'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['tv', "carpenter's kit", 'tool kit'],
['tv', "carpenter's kit", 'tool kit'],
['tv', "carpenter's kit", 'tool kit'],
['tv', 'espresso maker'],
['tv', 'pay-phone', 'pay-station'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', "potter's wheel"],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', "potter's wheel"],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['potted plant', 'pot', 'flowerpot'],
['tv', "carpenter's kit", 'tool kit'],
['tv', "carpenter's kit", 'tool kit'],
['tv', "carpenter's kit", 'tool kit'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['chair', 'desk'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['potted plant', 'pot', 'flowerpot'],
['laptop', 'notebook', 'notebook computer'],
['chair', 'desk']
]

sample_coco = ['Bag', 'backpack', 'handbag', 'suitcase', 'umbrella', 'tie', 'Animal', 'bird', 'cat', 'dog', 'horse',
               'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'Food', 'banana', 'apple', 'orange', 'carrot',
               'broccoli', 'cake', 'pizza', 'hot dog', 'donut', 'sandwich', 'Sports', 'tennis racket',
               'badminton racket', 'baseball bat', 'kite', 'snowboard', 'ball', 'basketball', 'Furniture', 'chair',
               'sofa', 'bed', 'toilet', 'couch', 'fridge', 'Office', 'keyboard', 'mouse', 'cellphone', 'tv', 'laptop',
               'Miscellaneous', 'Book', 'clock']

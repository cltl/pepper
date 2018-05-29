from datetime import date

statements = [
    {  # Lenka is from Serbia
        "subject": {
            "label": "Lenka",
            "type": "Person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Serbia",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 1,
        "position": "0-27",
        "date": date.today()
    },
    {  # Bram is from the Netherlands
        "subject": {
            "label": "Bram",
            "type": "Person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Netherlands",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 2,
        "position": "0-27",
        "date": date.today()
    },
    {  # Selene is from Mexico
        "subject": {
            "label": "Selene",
            "type": "Person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Mexico",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 3,
        "position": "0-27",
        "date": date.today()
    },
    {  # Piek is from the Netherlands
        "subject": {
            "label": "Piek",
            "type": "Person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Netherlands",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 4,
        "position": "0-27",
        "date": date.today()
    },
    {  # Selene K is from the Netherlands
        "subject": {
            "label": "Selene K",
            "type": "Person"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Netherlands",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 5,
        "position": "0-27",
        "date": date.today()
    },
    {  # Bram likes goulash
        "subject": {
            "label": "Bram",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "goulash",
            "type": "Dish"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 6,
        "position": "0-25",
        "date": date.today()
    },
    {  # Bram likes The Big Lebowski
        "subject": {
            "label": "Bram",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "the big lebowski",
            "type": "Movie"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 7,
        "position": "0-25",
        "date": date.today()
    },
    {  # Bram likes baseball
        "subject": {
            "label": "Bram",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "baseball",
            "type": "Sport"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 8,
        "position": "0-25",
        "date": date.today()
    },
    {  # Bram likes romantic movies
        "subject": {
            "label": "Bram",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "romantic movies",
            "type": "Film_Genre"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 9,
        "position": "0-25",
        "date": date.today()
    },
    {  # Lenka likes ice cream
        "subject": {
            "label": "Lenka",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "ice cream",
            "type": "Dish"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 10,
        "position": "0-25",
        "date": date.today()
    },
    {  # Lenka likes Harry Potter
        "subject": {
            "label": "Lenka",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "harry potter",
            "type": "Movie"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 11,
        "position": "0-25",
        "date": date.today()
    },
    {  # Lenka likes acrobatics
        "subject": {
            "label": "Lenka",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "acrobatics",
            "type": "Sport"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 12,
        "position": "0-25",
        "date": date.today()
    },
    {  # Lenka likes action movies
        "subject": {
            "label": "Lenka",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "action movies",
            "type": "Film_Genre"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 13,
        "position": "0-25",
        "date": date.today()
    },
    {  # Piek likes balkenbrij
        "subject": {
            "label": "Piek",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "balkenbrij",
            "type": "Dish"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 14,
        "position": "0-25",
        "date": date.today()
    },
    {  # Piek likes 2001 A Space Odyssey
        "subject": {
            "label": "Piek",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "2001 a space odyssey",
            "type": "Movie"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 15,
        "position": "0-25",
        "date": date.today()
    },
    {  # Piek likes soccer
        "subject": {
            "label": "Piek",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "soccer",
            "type": "Sport"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 16,
        "position": "0-25",
        "date": date.today()
    },
    {  # Piek likes horror movies
        "subject": {
            "label": "Piek",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "horror movies",
            "type": "Film_Genre"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 17,
        "position": "0-25",
        "date": date.today()
    },
    {  # Selene likes tacos
        "subject": {
            "label": "Selene",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "tacos",
            "type": "Dish"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 18,
        "position": "0-25",
        "date": date.today()
    },
    {  # Selene likes Coco
        "subject": {
            "label": "Selene",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "coco",
            "type": "Movie"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 19,
        "position": "0-25",
        "date": date.today()
    },
    {  # Selene likes soccer
        "subject": {
            "label": "Selene",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "soccer",
            "type": "Sport"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 20,
        "position": "0-25",
        "date": date.today()
    },
    {  # Selene likes animated movies
        "subject": {
            "label": "Selene",
            "type": "Person"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "animated movies",
            "type": "Film_Genre"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 21,
        "position": "0-25",
        "date": date.today()
    },
    {  # Bram knows Lenka
        "subject": {
            "label": "Bram",
            "type": "Person"
        },
        "predicate": {
            "type": "knows"
        },
        "object": {
            "label": "Lenka",
            "type": "Person"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 22,
        "position": "0-16",
        "date": date.today()
    },
    {  # Leolani is from France
        "subject": {
            "label": "Leolani",
            "type": "Robot"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "France",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 23,
        "position": "0-27",
        "date": date.today()
    },
    {  # Leolani is from Japan
        "subject": {
            "label": "Leolani",
            "type": "Robot"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Japan",
            "type": "Location"
        },
        "author": "Selene",
        "chat": 1,
        "turn": 24,
        "position": "0-27",
        "date": date.today()
    },
    {  # Lenka mother is ljubica (Lenka)
        u'predicate': {u'type': u'mother_is'},
        u'chat': u'',
        u'author': u'Lenka',
        u'object': {u'type': u'', u'id': u'', u'label': u'ljubica'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Lenka'}
    },
    {  # Bram likes action movies (Bram)
        u'predicate': {u'type': u'likes'},
        u'chat': u'',
        u'author': u'Bram',
        u'object': {u'type': u'', u'id': u'', u'label': u'action movies'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Bram'}
    },
    {  # Bram likes romantic movies (Selene)
        u'predicate': {u'type': u'likes'},
        u'chat': u'',
        u'author': u'Selene',
        u'object': {u'type': u'', u'id': u'', u'label': u'romantic movies'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Bram'}
    },
    {  # Bram is_from Italy (Selene)
        u'predicate': {u'type': u'is_from'},
        u'chat': u'',
        u'author': u'Selene',
        u'object': {u'type': u'Location', u'id': u'', u'label': u'Italy'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Bram'}
    },
    {  # Lenka favorite food-is cake (Lenka)
        u'predicate': {u'type': u'favorite'},
        u'chat': u'',
        u'author': u'Lenka',
        u'object': {u'type': u'', u'id': u'', u'label': u'cake'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Lenka'}
    }
]

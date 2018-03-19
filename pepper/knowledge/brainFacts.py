from datetime import date

statements = [
    {  # lenka is from Serbia
        "subject": {
            "label": "lenka",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "serbia",
            "type": "LOCATION"
        },
        "author": "selene",
        "chat": 1,
        "turn": 1,
        "position": "0-27",
        "date": date.today()
    },
    {  # bram is from the Netherlands
        "subject": {
            "label": "bram",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "netherlands",
            "type": "LOCATION"
        },
        "author": "selene",
        "chat": 1,
        "turn": 2,
        "position": "0-27",
        "date": date.today()
    },
    {  # selene is from Mexico
        "subject": {
            "label": "selene",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "mexico",
            "type": "LOCATION"
        },
        "author": "selene",
        "chat": 1,
        "turn": 3,
        "position": "0-27",
        "date": date.today()
    },
    {  # piek is from the Netherlands
        "subject": {
            "label": "piek",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "netherlands",
            "type": "LOCATION"
        },
        "author": "selene",
        "chat": 1,
        "turn": 4,
        "position": "0-27",
        "date": date.today()
    },
    {  # selene K is from the Netherlands
        "subject": {
            "label": "selene K",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "netherlands",
            "type": "LOCATION"
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "goulash",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "the big lebowski",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "baseball",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "romantic movies",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "ice cream",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "harry potter",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "acrobatics",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "action movies",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "balkenbrij",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "2001 a space odyssey",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "soccer",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "horror movies",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "tacos",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "coco",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "soccer",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "likes"
        },
        "object": {
            "label": "animated movies",
            "type": ""
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
            "type": "PERSON"
        },
        "predicate": {
            "type": "knows"
        },
        "object": {
            "label": "lenka",
            "type": "PERSON"
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
            "type": "ROBOT"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "france",
            "type": "LOCATION"
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
            "type": "ROBOT"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "japan",
            "type": "LOCATION"
        },
        "author": "selene",
        "chat": 1,
        "turn": 24,
        "position": "0-27",
        "date": date.today()
    },
    {  # lenka mother is ljubica (lenka)
        u'predicate': {u'type': u'mother-is'},
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
        u'object': {u'type': u'', u'id': u'', u'label': u'action movies'},
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
        u'object': {u'type': u'', u'id': u'', u'label': u'romantic movies'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # bram isFrom Italy (selene)
        u'predicate': {u'type': u'isFrom'},
        u'chat': u'',
        u'author': u'selene',
        u'object': {u'type': u'', u'id': u'', u'label': u'italy'},
        u'turn': u'',
        u'utterance_type': u'statement',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # lenka favorite food-is cake (lenka)
        u'predicate': {u'type': u'favorite food-is'},
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

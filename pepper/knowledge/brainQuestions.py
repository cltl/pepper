from datetime import date

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
        u'subject': {u'type': u'', u'id': u'', u'label': u'Bram'}},
    {  # Who is from the Serbia? -> Lenka, Selene
        "subject": {
            "label": "",
            "type": "PERSON"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Serbia",
            "type": "LOCATION"
        }
    },
    {  # Where is Lenka from? -> Serbia, Selene
        "subject": {
            "label": "Lenka",
            "type": "PERSON"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "",
            "type": "LOCATION"
        }
    },
    {  # Does Selene know Piek? -> (yes) Selene
        "subject": {
            "label": "Selene",
            "type": "PERSON"
        },
        "predicate": {
            "type": "knows"
        },
        "object": {
            "label": "Piek",
            "type": "PERSON"
        }
    },
    {  # Is Bram from the Netherlands? -> (idk) empty
        "subject": {
            "label": "Bram",
            "type": "PERSON"
        },
        "predicate": {
            "type": "is_from"
        },
        "object": {
            "label": "Netherlands",
            "type": "LOCATION"
        }
    },
    {  # Bram knows Beyonce
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
        u'subject': {u'type': u'', u'id': u'', u'label': u'Bram'}
    },
    {  # Leolani knows Bram
        u'predicate': {u'type': u'knows'}, u'chat': u'', u'author': u'Bram',
        u'object': {u'type': u'PERSON', u'id': u'', u'label': u'Bram'}, u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'leolani'}
    },
    {  # Selene knows Piek
        u'predicate': {u'type': u'knows'}, u'chat': u'', u'author': u'person',
        u'object': {u'type': u'PERSON', u'id': u'', u'label': u'Piek'}, u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Selene'}
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
    {  # what does Piek like (jo)
        u'predicate': {u'type': u'likes'},
        u'chat': u'',
        u'author': u'jo',
        u'object': {u'type': u'', u'id': u'', u'label': u''},
        u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19),
        u'position': u'',
        u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'Piek'}
    }
]

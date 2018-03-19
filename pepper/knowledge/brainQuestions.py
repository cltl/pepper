from datetime import date

questions = [
    {  # Who is from the Serbia? -> Lenka, Selene
        "subject": {
            "label": "",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "serbia",
            "type": "LOCATION"
        }
    },
    {  # Where is Lenka from? -> Serbia, Selene
        "subject": {
            "label": "lenka",
            "type": "PERSON"
        },
        "predicate": {
            "type": "isFrom"
        },
        "object": {
            "label": "",
            "type": "LOCATION"
        }
    },
    {  # Does Selene know Piek? -> (yes) Selene
        "subject": {
            "label": "selene",
            "type": "PERSON"
        },
        "predicate": {
            "type": "knows"
        },
        "object": {
            "label": "piek",
            "type": "PERSON"
        }
    },
    {  # Is Bram from the Netherlands? -> (idk) empty
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
        u'subject': {u'type': u'', u'id': u'', u'label': u'bram'}
    },
    {  # Leolani knows Bram
        u'predicate': {u'type': u'knows'}, u'chat': u'', u'author': u'bram',
        u'object': {u'type': u'PERSON', u'id': u'', u'label': u'bram'}, u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'leolani'}
    },
    {  # Selene knows Piek
        u'predicate': {u'type': u'knows'}, u'chat': u'', u'author': u'person',
        u'object': {u'type': u'PERSON', u'id': u'', u'label': u'piek'}, u'turn': u'',
        u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'selene'}
    },
    {  # Where is Leolani from?
        u'predicate': {u'type': u'isFrom'}, u'chat': u'', u'author': u'person',
        u'object': {u'type': u'', u'id': u'', u'label': u''}, u'turn': u'', u'utterance_type': u'question',
        u'date': date(2018, 3, 19), u'position': u'', u'response': {u'role': u'', u'format': u''},
        u'subject': {u'type': u'', u'id': u'', u'label': u'leolani'}
    },
    {  # Who is from italy
        u'predicate': {u'type': u'isFrom'}, u'chat': u'', u'author': u'jill',
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

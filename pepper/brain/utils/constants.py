"""
Other agreements/notes
    Labels are connected by a -
    Statements are hashed to be connected by a _
"""

NAMESPACE_MAPPING = {
    'Instance': 'GAF',
    'Assertion': 'GAF',
    'Statement': 'GRASP',
    'Experience': 'GRASP',
    'Chat': 'GRASP',
    'Visual': 'GRASP',
    'Utterance': 'GRASP',
    'Detection': 'GRASP',
    'Mention': 'GAF',
    'Attribution': 'GRASP',
    'AttributionValue': 'GRASP',
    'FactualityValue': 'GRASPf',
    'CertaintyValue': 'GRASPf',
    'TemporalValue': 'GRASPf',
    'PolarityValue': 'GRASPf',
    'SentimentValue': 'GRASPs',
    'EmotionValue': 'GRASPe',
    'Source': 'GRASP',
    'Actor': 'SEM',
    'Event': 'SEM',
    'Place': 'SEM',
    'Time': 'SEM',
    'DateTimeDescription': 'TIME',
    'Context': 'EPS'
}

CAPITALIZED_TYPES = ['person']

NOT_TO_MENTION_TYPES = ['instance']

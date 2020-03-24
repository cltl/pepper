"""
Other agreements/notes
    Labels are connected by a -
    Statements are hashed to be connected by a _
"""

NAMESPACE_MAPPING = {
    'Instance': 'GRASP',
    'Statement': 'GRASP',
    'Experience': 'GRASP',
    'Chat': 'GRASP',
    'Visual': 'GRASP',
    'Utterance': 'GRASP',
    'Detection': 'GRASP',
    'Mention': 'GRASP',
    'Attribution': 'GRASP',
    'AttributionValue': 'GRASP',
    'FactualityValue': 'GRASP',
    'CertaintyValue': 'GRASP',
    'TemporalValue': 'GRASP',
    'PolarityValue': 'GRASP',
    'SentimentValue': 'GRASP',
    'EmotionValue': 'GRASP',
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

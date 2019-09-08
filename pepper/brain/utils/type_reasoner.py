from pepper.brain.utils.helper_functions import read_query, casefold_text
from pepper.brain.basic_brain import BasicBrain

from pepper import config

from fuzzywuzzy import process
import requests


class TypeReasoner(BasicBrain):

    def __init__(self, address=config.BRAIN_URL_LOCAL, clear_all=False):
        # type: () -> TypeReasoner
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        super(TypeReasoner, self).__init__(address, clear_all, quiet=True)

    def reason_entity_type(self, item, exact_only=True):
        """
        Main function to determine if this item can be recognized by the brain, learned, or none
        Parameters
        ----------
        item: str
        exact_only: bool

        Returns
        -------

        """

        # Clean label
        articles = ['a-']
        for a in articles:
            if item.startswith(a):
                item = item.replace(a, '')

        if casefold_text(item, format='triple') in self.get_classes():
            # If this is in the ontology already as a class, create sensor triples directly
            text = 'I know about %s. I will remember this object' % item
            return item, text

        temp = self.get_labels_and_classes()
        if casefold_text(item, format='triple') in temp.keys():
            # If this is in the ontology already as a label, create sensor triples directly
            text = ' I know about %s. It is of type %s. I will remember this object' % (item, temp[item])
            return temp[item], text

        # Query the display for information
        class_type, description = self._exact_match_wikidata(item)
        if class_type is not None:
            # Had to learn it, but I can create triples now
            text = ' I did not know what %s is, but I searched on Wikidata and I found that it is a %s. ' \
                   'I will remember this object' % (item, class_type)
            return casefold_text(class_type, format='triple'), text

        class_type, description = self._exact_match_dbpedia(item)
        if class_type is not None:
            # Had to learn it, but I can create triples now
            text = ' I did not know what %s is, but I searched on Dbpedia and I found that it is a %s. ' \
                   'I will remember this object' % (item, class_type)
            return casefold_text(class_type, format='triple'), text

        if not exact_only:
            # Second go at dbpedia, relaxed approach
            class_type, description = self._keyword_match_dbpedia(item)
            if class_type is not None:
                # Had to really search for it to learn it, but I can create triples now
                text = ' I did not know what %s is, but I searched for fuzzy matches on the web and I found that it ' \
                       'is a %s. I will remember this object' % (item, class_type)
                return casefold_text(class_type, format='triple'), text

        # Failure, nothing found
        text = ' I am sorry, I could not learn anything on %s so I will not remember it' % item
        return None, text

    def _exact_match_dbpedia(self, item):
        """
        Query dbpedia for information on this item to get it's semantic type and description.
        :param item:
        :return:
        """
        # Gather combinations
        combinations = [item, item.capitalize(), item.lower(), item.title()]

        for comb in combinations:
            # Try exact matching query
            query = read_query('typing/dbpedia_type_and_description') % comb
            response = self._submit_query(query)

            # break if we have a hit
            if response:
                break

        class_type = response[0]['label_type']['value'] if response else None
        description = response[0]['description']['value'].split('.')[0] if response else None

        return class_type, description

    @staticmethod
    def _keyword_match_dbpedia(item):
        # Query API
        r = requests.get('http://lookup.dbpedia.org/api/search.asmx/KeywordSearch',
                         params={'QueryString': item, 'MaxHits': '10'},
                         headers={'Accept': 'application/json'}).json()['results']

        # Fuzzy match
        choices = [e['label'] for e in r]
        best_match = process.extractOne("item", choices)

        # Get best match object
        r = [{'label': e['label'], 'classes': e['classes'], 'description': e['description']} for e in r if
             e['label'] == best_match[0]]

        if r:
            r = r[0]

            if r['classes']:
                # process dbpedia classes only
                r['classes'] = [c['label'] for c in r['classes'] if 'dbpedia' in c['uri']]

        else:
            r = {'label': None, 'classes': None, 'description': None}

        return r['classes'][0] if r['classes'] else None, r['description'].split('.')[0] if r['description'] else None

    @staticmethod
    def _exact_match_wikidata(item):
        """
        Query wikidata for information on this item to get it's semantic type and description.
        :param item:
        :return:
        """
        url = 'https://query.wikidata.org/sparql'

        # Gather combinations
        combinations = [item, item.capitalize(), item.lower(), item.title()]

        for comb in combinations:
            # Try exact matching query
            query = read_query('typing/wikidata_type_and_description') % comb
            try:
                r = requests.get(url, params={'format': 'json', 'query': query}, timeout=3)
                data = r.json() if r.status_code != 500 else None
            except:
                data = None

            # break if we have a hit
            if data:
                break

        if data is not None:
            class_type = data[u'results'][u'bindings'][0][u'itemtypeLabel'][u'value'] \
                if 'itemtypeLabel' in data[u'results'][u'bindings'][0].keys() else None
            description = data[u'results'][u'bindings'][0][u'itemDescription'][u'value'] \
                if 'itemDescription' in data[u'results'][u'bindings'][0].keys() else None

            return class_type, description

        else:
            return None, None

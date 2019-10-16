from pepper.brain.utils.helper_functions import read_query, casefold_text
from pepper.brain.long_term_memory import LongTermMemory

import requests


class FameAwareMemory(LongTermMemory):
    def __init__(self, address="http://localhost:7200/repositories/famous", clear_all=False):
        # type: (str, bool) -> FameAwareMemory
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        super(FameAwareMemory, self).__init__(address, clear_all)

    def lookup_person_wikidata(self, person_name):
        """
        Query wikidata for information on this item to get it's semantic type and description.
        :param item:
        :return:
        """
        url = 'https://query.wikidata.org/sparql'

        # Gather combinations
        combinations = [person_name, person_name.capitalize(), person_name.lower(), person_name.title()]
        data = []

        for comb in combinations:
            # Try exact matching query
            query = read_query('famous_person') % (comb, comb, comb)
            try:
                r = requests.get(url, params={'format': 'json', 'query': query}, timeout=3)
                data = r.json() if r.status_code != 500 else None
            except:
                data = None

            # break if we have a hit
            if data and data['results']['bindings']:
                break

        if data is not None and data['results']['bindings']:
            # Report on size of graph found
            total_triples = len(data['results']['bindings'])
            self._log.info("{} triples found for {}".format(total_triples, comb))

            for triple in data['results']['bindings']:
                # Parse subject
                s_preprocessed_types = self._rdf_builder.clean_aggregated_types(triple['subjectTypesLabel']['value'])
                s = self._rdf_builder.fill_entity(casefold_text(triple['subjectLabel']['value'], format='triple'),
                                                  s_preprocessed_types, uri=triple['subject']['value'])
                self._link_entity(s, self.instance_graph)

                # Parse predicate
                p = self._rdf_builder.fill_predicate(casefold_text(triple['propLabel']['value'], format='triple'),
                                                     uri=triple['property']['value'])

                # Parse object
                if 'literal' not in triple['objectTypesLabel']['value']:
                    o_preprocessed_types = self._rdf_builder.clean_aggregated_types(triple['objectTypesLabel']['value'])
                    o = self._rdf_builder.fill_entity(casefold_text(triple['objectLabel']['value'], format='triple'),
                                                      o_preprocessed_types, uri=triple['object']['value'])
                    self._link_entity(o, self.instance_graph)
                    # Add claim to the dataset
                    self._create_claim_graph(s, p, o)
                else:
                    o = self._rdf_builder.fill_literal(casefold_text(triple['objectLabel']['value'], format='triple'))
                    # TODO: special logic for alternative labels

            # Finish process of uploading new knowledge to the triple store
            data = self._serialize(self._brain_log)
            code = self._upload_to_brain(data)

            output = {'response': code, 'label': person_name}

        else:
            output = {'response': None, 'label': person_name}

        return output

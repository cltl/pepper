from pepper.brain.utils.helper_functions import read_query, casefold_text
from pepper.brain.basic_brain import BasicBrain

from pepper import config


class LocationReasoner(BasicBrain):

    def __init__(self, address=config.BRAIN_URL_LOCAL, clear_all=False):
        # type: (str, bool) -> LocationReasoner
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        super(LocationReasoner, self).__init__(address, clear_all, is_submodule=True)

    @staticmethod
    def _measure_detection_overlap(detections_1, detections_2):
        if detections_1 == detections_2:
            return 1.0
        else:
            try:
                overlap = [value for value in detections_1 if value in detections_2]
                overlap = float(2 * len(overlap)) / float(len(detections_1) + len(detections_2))
                return float(overlap)
            except:
                return 0.0

    def _fill_episodic_memory_(self, raw_episode):
        """
        Structure overlap to get the provenance and entity on which they overlap
        Parameters
        ----------
        raw_episode: dict
            standard row result from SPARQL

        Returns
        -------
            Overlap object containing an entity and the provenance of the mention causing the overlap
        """
        preprocessed_date = self._rdf_builder.label_from_uri(raw_episode['date']['value'], 'LC')
        preprocessed_detections = self._rdf_builder.clean_aggregated_detections(raw_episode['detections']['value'])
        preprocessed_geo = self._rdf_builder.clean_aggregated_detections(raw_episode['geo']['value'])

        return {'context': raw_episode['cl']['value'], 'place': raw_episode['pl']['value'], 'date': preprocessed_date,
                'detections': preprocessed_detections, 'geo': preprocessed_geo}

    def get_episodic_memory(self):
        # Role as subject
        query = read_query('context/detections_per_context')
        response = self._submit_query(query)

        if response[0]['detections']['value'] != '':
            episodic_memory = [self._fill_episodic_memory_(elem) for elem in response]
        else:
            episodic_memory = []

        return episodic_memory

    def _fill_location_memory_(self, raw_objects_in_location):
        """
        Structure overlap to get the provenance and entity on which they overlap
        Parameters
        ----------
        raw_objects_in_location: dict
            list of ids and types for these ids

        Returns
        -------
            Overlap object containing an entity and the provenance of the mention causing the overlap
        """

        preprocessed_types = self._rdf_builder.clean_aggregated_types(raw_objects_in_location['type']['value'])
        preprocessed_ids = raw_objects_in_location['ids']['value'].split('|')

        return preprocessed_types, preprocessed_ids

    def get_location_memory(self, cntxt):
        # brain object memories
        query = read_query('context/ranked_object_ids_per_type') % 'cntxt.location.label'
        response = self._submit_query(query)

        location_memory = {}
        if response[0]['type']['value'] != '':
            for elem in response:
                categories, ids = self._fill_location_memory_(elem)
                # assign multiple categories (eg selene is person and agent)
                for category in categories:
                    temp = location_memory.get(casefold_text(category, format='triple'),
                                               {'brain_ids': [], 'local_ids': []})
                    temp['brain_ids'].extend(ids)
                    location_memory[casefold_text(category, format='triple')] = temp

        # Local object memories
        for item in cntxt.objects: # Error, this skips the first element?
            if item.name.lower() != 'person':
                temp = location_memory.get(casefold_text(item.name, format='triple'),
                                           {'brain_ids': [], 'local_ids': []})
                temp['local_ids'].append(str(item.id))
                location_memory[casefold_text(item.name, format='triple')] = temp

        # Merge giving priority to brain elements
        for cat, ids in location_memory.items():
            all_ids = ids['brain_ids'][:]
            all_ids.extend(ids['local_ids'])
            ids['ids'] = all_ids

        return location_memory

    def reason_location(self, cntxt):
        if cntxt.location.label != cntxt.location.UNKNOWN:
            return cntxt.location.label

        # Query all locations and detections (through context)
        memory = self.get_episodic_memory()

        if memory:
            # Generate set of current detections
            observations = []
            for item in cntxt.objects:
                if item.name.lower() != 'person':
                    observations.append(casefold_text(item.name, format='triple'))
            for item in cntxt.people:
                if item.name.lower() != item.UNKNOWN.lower():
                    observations.append(casefold_text(item.name, format='triple'))
            observations.append(cntxt.location.city)
            observations.append(cntxt.location.country)
            observations.append(cntxt.location.region)

            # Compare one by one and determine most similar
            for mem in memory:
                all = mem['detections']
                all.extend(mem['geo'])
                mem['overlap'] = self._measure_detection_overlap(all, observations)

            # Pick most similar and determine equality based on a threshold
            memory.sort(key=lambda x: x['overlap'])
            best_guess = memory[0]
            return best_guess['place'] if best_guess['overlap'] > 0.5 \
                                          and best_guess['place'] != cntxt.location.UNKNOWN else None

        else:
            return None

    def set_location_label(self, label, default='Unknown'):
        # https: // www.semanticarts.com / sparql - changing - instance - uris /
        # Replace as subject, replace label, replace as object in the database (long term memory)

        queries = read_query('context/rename_location') % (default, label,
                                                           default, default, default, default, label,
                                                           default, label)
        for query in queries.split(';'):
            response = self._submit_query(query, post=True)

        return None

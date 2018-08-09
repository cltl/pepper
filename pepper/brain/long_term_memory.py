from pepper import config
from pepper.brain.utils.helper_functions import hash_statement_id, casefold_label

from rdflib import Dataset, URIRef, Literal, Namespace, RDF, RDFS, OWL
from iribaker import to_iri
from SPARQLWrapper import SPARQLWrapper, JSON

import requests
import logging


class LongTermMemory(object):

    ONE_TO_ONE_PREDICATES = ['age', 'born_in', 'faceID', 'favorite', 'favorite_of', 'id', 'is_from', 'manufactured_in',
                             'mother_is', 'name']

    def __init__(self, address=config.LOCAL_BRAIN):
        """
        Interact with Triple store

        Parameters
        ----------
        address: str
            IP address and port of the Triple store
        """

        self.address = address
        self.namespaces = {}
        self.ontology_paths = {}
        self.format = 'trig'
        self.dataset = Dataset()
        self.query_prefixes = """
                    prefix gaf: <http://groundedannotationframework.org/gaf#> 
                    prefix grasp: <http://groundedannotationframework.org/grasp#> 
                    prefix leolaniInputs: <http://cltl.nl/leolani/inputs/>
                    prefix leolaniFriends: <http://cltl.nl/leolani/friends/> 
                    prefix leolaniTalk: <http://cltl.nl/leolani/talk/> 
                    prefix leolaniTime: <http://cltl.nl/leolani/time/> 
                    prefix leolaniWorld: <http://cltl.nl/leolani/world/> 
                    prefix n2mu: <http://cltl.nl/leolani/n2mu/> 
                    prefix ns1: <urn:x-rdflib:> 
                    prefix owl: <http://www.w3.org/2002/07/owl#> 
                    prefix prov: <http://www.w3.org/ns/prov#> 
                    prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
                    prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
                    prefix sem: <http://semanticweb.cs.vu.nl/2009/11/sem/> 
                    prefix skos: <http://www.w3.org/2004/02/skos/core#> 
                    prefix time: <http://www.w3.org/TR/owl-time/#> 
                    prefix xml: <http://www.w3.org/XML/1998/namespace> 
                    prefix xml1: <https://www.w3.org/TR/xmlschema-2/#> 
                    prefix xsd: <http://www.w3.org/2001/XMLSchema#>
                    """

        self._define_namespaces()
        self._get_ontology_path()
        self._bind_namespaces()

        self.my_uri = None

        self._log = logging.getLogger(self.__class__.__name__)
        self._log.debug("Booted")

    #################################### Main functions to interact with the brain ####################################

    def update(self, capsule):
        """
        Main function to interact with if a statement is coming into the brain. Takes in a structured parsed statement,
        transforms them to triples, and posts them to the triple store
        :param statement: Structured data of a parsed statement
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Create graphs and triples
        self._model_graphs_(capsule)

        data = self._serialize(config.BRAIN_LOG)

        code = self._upload_to_brain(data)

        # Create JSON output
        capsule["date"] = str(capsule["date"])
        output = {'response': code, 'statement': capsule}

        return output

    def experience(self, experience):
        """
        Main function to interact with if a statement is coming into the brain. Takes in a structured parsed statement,
        transforms them to triples, and posts them to the triple store
        :param experience: Structured data of a parsed statement
        :return: json response containing the status for posting the triples, and the original statement
        """
        # Create graphs and triples
        self._model_sensor_graphs_(experience)

        data = self._serialize(config.BRAIN_LOG)

        code = self._upload_to_brain(data)

        # Create JSON output
        experience["date"] = str(experience["date"])
        output = {'response': code, 'statement': experience}

        return output

    def query_brain(self, question):
        """
        Main function to interact with if a question is coming into the brain. Takes in a structured parsed question,
        transforms it into a query, and queries the triple store for a response
        :param question: Structured data of a parsed question
        :return: json response containing the results of the query, and the original question
        """
        # Generate query
        query = self._create_query(question)

        # Perform query
        response = self._submit_query(query)

        # Create JSON output
        if 'date' in question.keys():
            question["date"] = str(question["date"])
        output = {'response': response, 'question': question}

        return output

    def process_visual(self, item):
        if item in self.get_classes():
            # If this is in the ontology already, create sensor triples directly
            print('I know about %s, I will remember this object' % item)
        else:
            # Query the web for information
            class_type, description = self.get_type_description(item)
            if class_type is not None:
                # Had to learn it, but I can create triples now
                print('I did not know what %s is, but I searched on the web and I found that it is a %s. '
                      'I will remember this object' % (item, class_type))
            else:
                # Failure, nothing found
                print('I am sorry, I could not learn anything on %s so I will not remember it' % item)

    ########## management system for keeping track of chats and turns ##########
    def get_last_chat_id(self):
        """
        Get the id for the last interaction recorded
        :return: id
        """
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX grasp: <http://groundedannotationframework.org/grasp#>
            PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
            
            select ?chatid where { 
                ?chat rdf:type grasp:Chat .
                ?chat n2mu:id ?chatid .
            } ORDER BY DESC (?chatid) LIMIT 1
        """

        response = self._submit_query(query)

        if response:
            last_chat = int(response[0]['chatid']['value'])
        else:
            last_chat = 0

        return last_chat

    def get_last_turn_id(self, chat_id):
        """
        Get the id for the last turn in the given chat
        :param chat_id: id for chat of interest
        :return:  id
        """
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>

            select ?s where { 
            ?s rdf:type sem:Event .
            FILTER(regex(str(?s), "chat%s_turn")) .
            }
        """ % chat_id

        response = self._submit_query(query)

        last_turn = 0
        for turn in response:
            turn_uri = turn['s']['value']
            turn_id = turn_uri.split('/')[-1][10:]
            turn_id = int(turn_id)

            if turn_id > last_turn:
                last_turn = turn_id

        return last_turn

    ########## brain structure exploration ##########
    def get_predicates(self):
        query = """
            select distinct ?p where { 
            ?s ?p ?o .
            FILTER(regex(str(?p), "n2mu")) .
        } ORDER BY str(?p)
        """

        response = self._submit_query(query)
        predicates = [elem['p']['value'].split('/')[-1] for elem in response]

        return predicates

    def get_classes(self):
        query = """
            select distinct ?o where { 
            ?s a ?o .
            FILTER(regex(str(?o), "n2mu")) .
        } ORDER BY (str(?p))
        """

        response = self._submit_query(query)
        classes = [elem['o']['value'].split('/')[-1] for elem in response]

        return classes

    ########## learned facts exploration ##########
    def count_statements(self):
        """

        :return:
        """
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX grasp: <http://groundedannotationframework.org/grasp#>

            select (COUNT(?stat) AS ?count) where { 
            ?stat rdf:type grasp:Statement .
            }
        """

        response = self._submit_query(query)
        response = response[0]['count']['value']

        return response

    def count_friends(self):
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>

            select (COUNT(?act) AS ?count) where { 
            ?act rdf:type sem:Actor .
            }
        """

        response = self._submit_query(query)
        response = response[0]['count']['value']

        return response

    def get_my_friends(self):
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

            select distinct ?name where { 
                ?act rdf:type sem:Actor .
                ?act rdfs:label ?name
            }
        """

        response = self._submit_query(query)
        friends = [elem['name']['value'].split('/')[-1] for elem in response]

        return friends

    def get_best_friends(self):
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
            select distinct ?name (count(distinct ?chat) as ?num_chat) where { 
                ?act rdf:type sem:Actor .
                ?act rdfs:label ?name .
                ?chat sem:hasActor ?act .
                ?chat sem:hasSubevent ?t
            }    GROUP BY ?name
            ORDER BY DESC (?num_chat) 
            LIMIT 5
        """

        response = self._submit_query(query)
        best_friends = [elem['name']['value'] for elem in response]

        return best_friends

    def get_instance_of_type(self, instance_type):
        query = """
            PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            select distinct ?name where { 
                ?s a n2mu:%s .
                ?s rdfs:label ?name
            } 
        """ % instance_type

        response = self._submit_query(query)
        instances = [elem['name']['value'] for elem in response]

        return instances

    def when_last_chat_with(self, actor_label):
        query = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        
            select distinct ?time where { 
                ?act rdf:type sem:Actor .
                ?act rdfs:label "%s" .
                ?chat sem:hasActor ?act .
                ?chat sem:hasSubevent ?turn .
                ?chat sem:hasTime ?time
            }  ORDER BY DESC (?time)
            LIMIT 1
        """ % actor_label

        response = self._submit_query(query)
        response = response[0]['time']['value'].split('/')[-1]

        return response

    def get_triples_with_predicate(self, predicate):
        query = """
            PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            
            select ?sname ?oname where { 
                ?s n2mu:%s ?o .
                ?s rdfs:label ?sname .
                ?o rdfs:label ?oname
            }  
        """ % predicate

        response = self._submit_query(query)
        triples = [(elem['sname']['value'], elem['oname']['value']) for elem in response]

        return triples

    ########## conflicts ##########
    def get_all_conflicts(self):

        conflicts = []

        for predicate in self.ONE_TO_ONE_PREDICATES:
            conflicts.extend(self._get_conflicts_with_predicate(predicate))

        return conflicts

    ########## semantic web ##########
    def get_type_description(self, item):
        query = """
            PREFIX dbo: <http://dbpedia.org/ontology/>
            PREFIX dbr: <http://dbpedia.org/resource/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            SELECT DISTINCT ?label_type ?description
            WHERE {
                SERVICE <http://dbpedia.org/sparql> { 
                    ?thing rdf:type owl:Thing ;
                           rdfs:label "%s"@en ;
                           dbo:abstract ?description ;
                           rdf:type ?type .
                    ?type rdfs:label ?label_type
                filter(regex(str(?type), "dbpedia"))
                    filter(langMatches(lang(?description),"EN"))
                    filter(langMatches(lang(?label_type),"EN"))
                }
            }
            LIMIT 1
        """ % item

        response = self._submit_query(query)

        if response:
            class_type = response[0]['label_type']['value']
            description = response[0]['description']['value'].split('.')[0]
        else:
            class_type = None
            description = None

        return class_type, description

    ######################################## Helpers for setting up connection ########################################

    def _define_namespaces(self):
        """
        Define namespaces for different layers (ontology/vocab and resource). Assign them to self
        :return:
        """
        # Namespaces for the instance layer
        instance_vocab = 'http://cltl.nl/leolani/n2mu/'
        self.namespaces['N2MU'] = Namespace(instance_vocab)
        instance_resource = 'http://cltl.nl/leolani/world/'
        self.namespaces['LW'] = Namespace(instance_resource)

        # Namespaces for the mention layer
        mention_vocab = 'http://groundedannotationframework.org/gaf#'
        self.namespaces['GAF'] = Namespace(mention_vocab)
        mention_resource = 'http://cltl.nl/leolani/talk/'
        self.namespaces['LTa'] = Namespace(mention_resource)

        # Namespaces for the attribution layer
        attribution_vocab = 'http://groundedannotationframework.org/grasp#'
        self.namespaces['GRASP'] = Namespace(attribution_vocab)
        attribution_resource_friends = 'http://cltl.nl/leolani/friends/'
        self.namespaces['LF'] = Namespace(attribution_resource_friends)
        attribution_resource_inputs = 'http://cltl.nl/leolani/inputs/'
        self.namespaces['LI'] = Namespace(attribution_resource_inputs)

        # Namespaces for the temporal layer-ish
        time_vocab = 'http://www.w3.org/TR/owl-time/#'
        self.namespaces['TIME'] = Namespace(time_vocab)
        time_resource = 'http://cltl.nl/leolani/time/'
        self.namespaces['LTi'] = Namespace(time_resource)

        # The namespaces of external ontologies
        skos = 'http://www.w3.org/2004/02/skos/core#'
        self.namespaces['SKOS'] = Namespace(skos)

        prov = 'http://www.w3.org/ns/prov#'
        self.namespaces['PROV'] = Namespace(prov)

        sem = 'http://semanticweb.cs.vu.nl/2009/11/sem/'
        self.namespaces['SEM'] = Namespace(sem)

        xml = 'https://www.w3.org/TR/xmlschema-2/#'
        self.namespaces['XML'] = Namespace(xml)

    def _get_ontology_path(self):
        """
        Define ontology paths to key vocabularies
        :return:
        """
        self.ontology_paths['n2mu'] = './../../knowledge_representation/ontologies/leolani.ttl'
        self.ontology_paths['gaf'] = './../../knowledge_representation/ontologies/gaf.rdf'
        self.ontology_paths['grasp'] = './../../knowledge_representation/ontologies/grasp.rdf'
        self.ontology_paths['sem'] = './../../knowledge_representation/ontologies/sem.rdf'

    def _bind_namespaces(self):
        """
        Bnd namespaces
        :return:
        """
        self.dataset.bind('n2mu', self.namespaces['N2MU'])
        self.dataset.bind('leolaniWorld', self.namespaces['LW'])
        self.dataset.bind('gaf', self.namespaces['GAF'])
        self.dataset.bind('leolaniTalk', self.namespaces['LTa'])
        self.dataset.bind('grasp', self.namespaces['GRASP'])
        self.dataset.bind('leolaniFriends', self.namespaces['LF'])
        self.dataset.bind('leolaniInputs', self.namespaces['LI'])
        self.dataset.bind('time', self.namespaces['TIME'])
        self.dataset.bind('leolaniTime', self.namespaces['LTi'])
        self.dataset.bind('skos', self.namespaces['SKOS'])
        self.dataset.bind('prov', self.namespaces['PROV'])
        self.dataset.bind('sem', self.namespaces['SEM'])
        self.dataset.bind('xml', self.namespaces['XML'])
        self.dataset.bind('owl', OWL)

    ######################################## Helpers for statement processing ########################################

    def create_chat_id(self, actor, date):
        self._log.debug('Chat with {} on {}'.format(actor, date))

        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX grasp: <http://groundedannotationframework.org/grasp#>
                PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
                PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>
                PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                PREFIX time: <http://www.w3.org/TR/owl-time/#>
                
                select ?chatid ?day ?month ?year where { 
                    ?chat rdf:type grasp:Chat .
                    ?chat n2mu:id ?chatid .
                    ?chat sem:hasActor ?actor .
                    ?actor rdfs:label "%s" .
                    ?chat sem:hasTime ?time . 
                    ?time time:day ?day . 
                    ?time time:month ?month . 
                    ?time time:year ?year .
                    FILTER(!regex(str(?chat), "turn")) .
                } ORDER BY DESC (?chat)
                LIMIT 1
        """ % (actor)

        response = self._submit_query(query)

        if not response:
            # have never chatted with this person, so add one to latest chat
            chat_id = self.get_last_chat_id() + 1
        elif int(response[0]['day']['value']) == int(date.day) and int(response[0]['month']['value']) == int(date.month) and int(response[0]['year']['value']) == int(date.year):
            # Chatted with this person today so same chat id
            chat_id = int(response[0]['chatid']['value'])
        else:
            # have chatted with this person (either today or ever), so add one to latest chat
            chat_id = self.get_last_chat_id() + 1

        return chat_id

    def create_turn_id(self, chat_id):
        self._log.debug('Turn in chat {}'.format(chat_id))

        query = """
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                PREFIX grasp: <http://groundedannotationframework.org/grasp#>
                PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
                PREFIX sem: <http://semanticweb.cs.vu.nl/2009/11/sem/>

                select ?turnid where { 
                    ?chat rdf:type grasp:Chat .
                    ?chat n2mu:id "%s" .
                    ?chat sem:hasSubevent ?turn .
                    ?turn n2mu:id ?turnid .
                } ORDER BY DESC (?turnid)
                LIMIT 1
        """ % (chat_id)

        response = self._submit_query(query)

        if not response:
            # no turns in this chat, start from 1
            turn_id = 1
        else:
            # Add one to latest chat
            turn_id = int(response['turnid']['value']) + 1

        return turn_id

    def _generate_leolani(self, instance_graph):
        # Create Leolani
        leolani_id = 'Leolani'
        leolani_label = 'Leolani'

        leolani = URIRef(to_iri(self.namespaces['LW'] + leolani_id))
        leolani_label = Literal(leolani_label)
        leolani_type1 = URIRef(to_iri(self.namespaces['N2MU'] + 'Robot'))
        leolani_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((leolani, RDFS.label, leolani_label))
        instance_graph.add((leolani, RDF.type, leolani_type1))
        instance_graph.add((leolani, RDF.type, leolani_type2))

        self.my_uri = leolani

        return leolani

    def _create_leolani_world(self, parsed_statement):
        # Instance graph
        instance_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'Instances'))
        instance_graph = self.dataset.graph(instance_graph_uri)

        # Subject
        if parsed_statement['subject']['type'] == '':  # We only get the label
            subject_vocab = OWL
            subject_type = 'Thing'
        else:
            subject_vocab = self.namespaces['N2MU']
            subject_type = parsed_statement['subject']['type']

        subject_id = casefold_label(parsed_statement['subject']['label'])

        subject = URIRef(to_iri(self.namespaces['LW'] + subject_id))
        subject_label = Literal(subject_id)
        subject_type1 = URIRef(to_iri(subject_vocab + subject_type))
        subject_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((subject, RDFS.label, subject_label))
        instance_graph.add((subject, RDF.type, subject_type1))
        instance_graph.add((subject, RDF.type, subject_type2))

        # Object
        if parsed_statement['object']['type'] == '':  # We only get the label
            object_vocab = OWL
            object_type = 'Thing'
        else:
            object_vocab = self.namespaces['N2MU']
            object_type = parsed_statement['object']['type']

        object_id = casefold_label(parsed_statement['object']['label'])

        object = URIRef(to_iri(self.namespaces['LW'] + object_id))
        object_label = Literal(object_id)
        object_type1 = URIRef(to_iri(object_vocab + object_type))
        object_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((object, RDFS.label, object_label))
        instance_graph.add((object, RDF.type, object_type1))
        instance_graph.add((object, RDF.type, object_type2))

        claim_graph, statement = self._create_claim_graph(parsed_statement, subject, subject_label, object, object_label)

        return instance_graph, claim_graph, subject, object, statement

    def _create_claim_graph(self, parsed_statement, subject, subject_label, object, object_label):
        # Claim graph
        claim_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'Claims'))
        claim_graph = self.dataset.graph(claim_graph_uri)

        # Predicate
        predicate = parsed_statement['predicate']['type'].replace(" ", "_")

        # Statement
        statement_id = hash_statement_id([subject_label, predicate, object_label])

        statement = URIRef(to_iri(self.namespaces['LW'] + statement_id))
        statement_type1 = URIRef(to_iri(self.namespaces['GRASP'] + 'Statement'))
        statement_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))
        statement_type3 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))

        # Create graph and add triple
        graph = self.dataset.graph(statement)
        graph.add((subject, self.namespaces['N2MU'][predicate], object))

        claim_graph.add((statement, RDF.type, statement_type1))
        claim_graph.add((statement, RDF.type, statement_type2))
        claim_graph.add((statement, RDF.type, statement_type3))

        return claim_graph, statement

    def _create_leolani_talk(self, statement, leolani):
        # Interaction graph
        interaction_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Interactions'))
        interaction_graph = self.dataset.graph(interaction_graph_uri)

        # Time
        date = statement["date"]
        time = URIRef(to_iri(self.namespaces['LTi'] + str(statement["date"].isoformat())))
        time_type = URIRef(to_iri(self.namespaces['TIME'] + 'DateTimeDescription'))
        day = Literal(date.day, datatype=self.namespaces['XML']['gDay'])
        month = Literal(date.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = Literal(date.year, datatype=self.namespaces['XML']['gYear'])
        time_unitType = URIRef(to_iri(self.namespaces['TIME'] + 'unitDay'))

        interaction_graph.add((time, RDF.type, time_type))
        interaction_graph.add((time, self.namespaces['TIME']['day'], day))
        interaction_graph.add((time, self.namespaces['TIME']['month'], month))
        interaction_graph.add((time, self.namespaces['TIME']['year'], year))
        interaction_graph.add((time, self.namespaces['TIME']['unitType'], time_unitType))

        # Actor
        actor_id = statement['author']
        actor_label = statement['author']

        actor = URIRef(to_iri(to_iri(self.namespaces['LF'] + actor_id)))
        actor_label = Literal(actor_label)
        actor_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Actor'))
        actor_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        interaction_graph.add((actor, RDFS.label, actor_label))
        interaction_graph.add((actor, RDF.type, actor_type1))
        interaction_graph.add((actor, RDF.type, actor_type2))

        # Add leolani knows actor
        interaction_graph.add((leolani, self.namespaces['N2MU']['knows'], actor))

        # Chat and turn
        chat_id = self.create_chat_id(actor_label, date)
        chat_label = 'chat%s' % chat_id
        turn_id = self.create_turn_id(chat_id)
        turn_label = chat_label + '_turn%s' % turn_id

        turn = URIRef(to_iri(self.namespaces['LTa'] + turn_label))
        turn_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        turn_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Turn'))

        interaction_graph.add((turn, RDF.type, turn_type1))
        interaction_graph.add((turn, RDF.type, turn_type2))
        interaction_graph.add((turn, self.namespaces['N2MU']['id'], Literal(turn_id)))
        interaction_graph.add((turn, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((turn, self.namespaces['SEM']['hasTime'], time))

        chat = URIRef(to_iri(self.namespaces['LTa'] + chat_label))
        chat_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        chat_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Chat'))

        interaction_graph.add((chat, RDF.type, chat_type1))
        interaction_graph.add((chat, RDF.type, chat_type2))
        interaction_graph.add((chat, self.namespaces['N2MU']['id'], Literal(chat_id)))
        interaction_graph.add((chat, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((chat, self.namespaces['SEM']['hasTime'], time))
        interaction_graph.add((chat, self.namespaces['SEM']['hasSubevent'], turn))

        perspective_graph, mention, attribution = self._create_perspective_graph(statement, turn_label)

        # Link interactions and perspectives
        perspective_graph.add((mention, self.namespaces['GRASP']['wasAttributedTo'], actor))
        perspective_graph.add((mention, self.namespaces['GRASP']['hasAttribution'], attribution))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], chat))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], turn))

        return interaction_graph, perspective_graph, actor, time, mention, attribution

    def _create_perspective_graph(self, parsed_statement, turn_label):
        # Perspective graph
        perspective_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Perspectives'))
        perspective_graph = self.dataset.graph(perspective_graph_uri)

        # Mention
        mention_id = turn_label + '_char%s' % parsed_statement['position']
        mention = URIRef(to_iri(self.namespaces['LTa'] + mention_id))
        mention_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Mention'))

        perspective_graph.add((mention, RDF.type, mention_type))

        # Attribution
        attribution_id = mention_id + '_CERTAIN'
        attribution = URIRef(to_iri(self.namespaces['LTa'] + attribution_id))
        attribution_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Attribution'))
        attribution_value = URIRef(to_iri(self.namespaces['GRASP'] + 'CERTAIN'))

        perspective_graph.add((attribution, RDF.type, attribution_type))
        perspective_graph.add((attribution, RDF.value, attribution_value))

        return perspective_graph, mention, attribution

    def _serialize(self, file_path):
        """
        Save graph to local file and return the serialized string
        :param file_path: path to where data will be saved
        :return: serialized data as string
        """
        # Save to file but return the python representation
        with open(file_path + '.' + self.format, 'w') as f:
            self.dataset.serialize(f, format=self.format)
        return self.dataset.serialize(format=self.format)

    def _upload_to_brain(self, data):
        """
        Post data to the brain
        :param data: serialized data as string
        :return: response status
        """
        self._log.debug("Posting triples")

        # From serialized string
        post_url = self.address + "/statements"
        response = requests.post(post_url,
                                 data=data,
                                 headers={'Content-Type': 'application/x-' + self.format})

        return str(response.status_code)

    def _model_graphs_(self, capsule):
        # Leolani world (includes instance and claim graphs)
        instance_graph, claim_graph, subject, object, statement = self._create_leolani_world(capsule)

        # Identity
        leolani = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri

        # Leolani talk (includes interaction and perspective graphs)
        interaction_graph, perspective_graph, actor, time, mention, attribution = self._create_leolani_talk(capsule, leolani)

        # Interconnections
        instance_graph.add((subject, self.namespaces['GRASP']['denotedIn'], mention))
        instance_graph.add((object, self.namespaces['GRASP']['denotedIn'], mention))

        instance_graph.add((statement, self.namespaces['GRASP']['denotedBy'], mention))
        instance_graph.add((statement, self.namespaces['SEM']['hasActor'], actor))
        instance_graph.add((statement, self.namespaces['SEM']['hasTime'], time))

        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], subject))
        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], object))
        perspective_graph.add((mention, self.namespaces['GRASP']['denotes'], statement))

        perspective_graph.add((attribution, self.namespaces['GRASP']['isAttributionFor'], mention))

    ######################################### Helpers for question processing #########################################

    def _create_query(self, parsed_question):
        _ = hash_statement_id([parsed_question['subject']['label'], parsed_question['predicate']['type'], parsed_question['object']['label']])

        # Query subject
        if parsed_question['subject']['label'] == "":
            # Case fold
            # object_label = casefold_label(parsed_question['object']['label'])

            query = """
                SELECT ?slabel ?authorlabel
                        WHERE { 
                            ?s n2mu:%s ?o . 
                            ?s rdfs:label ?slabel . 
                            ?o rdfs:label '%s' .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['object']['label'],
                       parsed_question['predicate']['type'])

        # Query object
        elif parsed_question['object']['label'] == "":
            query = """
                SELECT ?olabel ?authorlabel
                        WHERE { 
                            ?s n2mu:%s ?o .   
                            ?s rdfs:label '%s' .  
                            ?o rdfs:label ?olabel .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['subject']['label'],
                       parsed_question['predicate']['type'])

        # Query existence
        else:
            query = """
                SELECT ?authorlabel ?v
                        WHERE { 
                            ?s n2mu:%s ?o .   
                            ?s rdfs:label '%s' .  
                            ?o rdfs:label '%s' .  
                            GRAPH ?g {
                                ?s n2mu:%s ?o . 
                            } . 
                            ?g grasp:denotedBy ?m . 
                            ?m grasp:wasAttributedTo ?author . 
                            ?author rdfs:label ?authorlabel .
                            ?m grasp:hasAttribution ?att .
                            ?att rdf:value ?v .
                        }
                """ % (parsed_question['predicate']['type'],
                       parsed_question['subject']['label'],
                       parsed_question['object']['label'],
                       parsed_question['predicate']['type'])

        query = self.query_prefixes + query

        return query

    def _submit_query(self, query):
        # Set up connection
        sparql = SPARQLWrapper(self.address)

        # Response parameters
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        sparql.addParameter('Accept', 'application/sparql-results+json')
        response = sparql.query().convert()

        return response["results"]["bindings"]

    ########################################## Helpers for sensor processing ##########################################
    def _create_leolani_world_sens(self, sensed_visual):
        # Instance graph
        instance_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'Instances'))
        instance_graph = self.dataset.graph(instance_graph_uri)

        # Subject
        leolani = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri

        # Object
        if sensed_visual['object']['type'] == '':  # We only get the label
            object_vocab = OWL
            object_type = 'Thing'
        else:
            object_vocab = self.namespaces['N2MU']
            object_type = sensed_visual['object']['type']

        object_id = casefold_label(sensed_visual['object']['label'])

        object = URIRef(to_iri(self.namespaces['LW'] + object_id))
        object_label = Literal(object_id)
        object_type1 = URIRef(to_iri(object_vocab + object_type))
        object_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        instance_graph.add((object, RDFS.label, object_label))
        instance_graph.add((object, RDF.type, object_type1))
        instance_graph.add((object, RDF.type, object_type2))

        claim_graph, experience = self._create_claim_graph_sens(leolani, 'Leolani', object, object_label)

        return instance_graph, claim_graph, leolani, object, experience

    def _create_claim_graph_sens(self, subject, subject_label, object, object_label):
        # Claim graph
        claim_graph_uri = URIRef(to_iri(self.namespaces['LW'] + 'Claims'))
        claim_graph = self.dataset.graph(claim_graph_uri)

        # Predicate
        predicate = 'saw'

        # Statement
        experience_id = hash_statement_id([subject_label, predicate, object_label])

        experience = URIRef(to_iri(self.namespaces['LW'] + experience_id))
        experience_type1 = URIRef(to_iri(self.namespaces['GRASP'] + 'Experience'))
        experience_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))
        experience_type3 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))

        # Create graph and add triple
        graph = self.dataset.graph(experience)
        graph.add((subject, self.namespaces['N2MU'][predicate], object))

        claim_graph.add((experience, RDF.type, experience_type1))
        claim_graph.add((experience, RDF.type, experience_type2))
        claim_graph.add((experience, RDF.type, experience_type3))

        return claim_graph, experience

    def _create_leolani_talk_sens(self, sensed_visual, leolani):
        # Interaction graph
        interaction_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Sensors'))
        interaction_graph = self.dataset.graph(interaction_graph_uri)

        # Time
        date = sensed_visual["date"]
        time = URIRef(to_iri(self.namespaces['LTi'] + str(sensed_visual["date"].isoformat())))
        time_type = URIRef(to_iri(self.namespaces['TIME'] + 'DateTimeDescription'))
        day = Literal(date.day, datatype=self.namespaces['XML']['gDay'])
        month = Literal(date.month, datatype=self.namespaces['XML']['gMonthDay'])
        year = Literal(date.year, datatype=self.namespaces['XML']['gYear'])
        time_unitType = URIRef(to_iri(self.namespaces['TIME'] + 'unitDay'))

        interaction_graph.add((time, RDF.type, time_type))
        interaction_graph.add((time, self.namespaces['TIME']['day'], day))
        interaction_graph.add((time, self.namespaces['TIME']['month'], month))
        interaction_graph.add((time, self.namespaces['TIME']['year'], year))
        interaction_graph.add((time, self.namespaces['TIME']['unitType'], time_unitType))

        # Actor
        actor_id = sensed_visual['author']
        actor_label = sensed_visual['author']

        actor = URIRef(to_iri(to_iri(self.namespaces['LI'] + actor_id)))
        actor_label = Literal(actor_label)
        actor_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Actor'))
        actor_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Instance'))

        interaction_graph.add((actor, RDFS.label, actor_label))
        interaction_graph.add((actor, RDF.type, actor_type1))
        interaction_graph.add((actor, RDF.type, actor_type2))

        # TODO Add leolani sensed event
        interaction_graph.add((leolani, self.namespaces['N2MU']['sense'], actor))

        # Chat and turn
        chat_id = self.create_chat_id(actor_label, date)
        chat_label = 'visual%s' % chat_id
        turn_id = self.create_turn_id(chat_id)
        turn_label = chat_label + '_object%s' % turn_id

        turn = URIRef(to_iri(self.namespaces['LTa'] + turn_label))
        turn_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        turn_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Object'))

        interaction_graph.add((turn, RDF.type, turn_type1))
        interaction_graph.add((turn, RDF.type, turn_type2))
        interaction_graph.add((turn, self.namespaces['N2MU']['id'], Literal(turn_id)))
        interaction_graph.add((turn, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((turn, self.namespaces['SEM']['hasTime'], time))

        chat = URIRef(to_iri(self.namespaces['LTa'] + chat_label))
        chat_type1 = URIRef(to_iri(self.namespaces['SEM'] + 'Event'))
        chat_type2 = URIRef(to_iri(self.namespaces['GRASP'] + 'Visual'))

        interaction_graph.add((chat, RDF.type, chat_type1))
        interaction_graph.add((chat, RDF.type, chat_type2))
        interaction_graph.add((chat, self.namespaces['N2MU']['id'], Literal(chat_id)))
        interaction_graph.add((chat, self.namespaces['SEM']['hasActor'], actor))
        interaction_graph.add((chat, self.namespaces['SEM']['hasTime'], time))
        interaction_graph.add((chat, self.namespaces['SEM']['hasSubevent'], turn))

        perspective_graph, mention, attribution = self._create_perspective_graph_sens(sensed_visual, turn_label)

        # Link interactions and perspectives
        perspective_graph.add((mention, self.namespaces['GRASP']['wasAttributedTo'], actor))
        perspective_graph.add((mention, self.namespaces['GRASP']['hasAttribution'], attribution))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], chat))
        perspective_graph.add((mention, self.namespaces['PROV']['wasDerivedFrom'], turn))

        return interaction_graph, perspective_graph, actor, time, mention, attribution

    def _create_perspective_graph_sens(self, sensed_visual, turn_label):
        # Perspective graph
        perspective_graph_uri = URIRef(to_iri(self.namespaces['LTa'] + 'Perspectives'))
        perspective_graph = self.dataset.graph(perspective_graph_uri)

        # Mention
        mention_id = turn_label + '_pixel%s' % sensed_visual['position']
        mention = URIRef(to_iri(self.namespaces['LTa'] + mention_id))
        mention_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Mention'))

        perspective_graph.add((mention, RDF.type, mention_type))

        # Attribution
        attribution_id = mention_id + '_CERTAIN'
        attribution = URIRef(to_iri(self.namespaces['LTa'] + attribution_id))
        attribution_type = URIRef(to_iri(self.namespaces['GRASP'] + 'Attribution'))
        attribution_value = URIRef(to_iri(self.namespaces['GRASP'] + 'CERTAIN'))

        perspective_graph.add((attribution, RDF.type, attribution_type))
        perspective_graph.add((attribution, RDF.value, attribution_value))

        return perspective_graph, mention, attribution

    def _model_sensor_graphs_(self, experience):
        # Leolani world (includes instance and claim graphs)
        instance_graph, claim_graph, subject, object, statement = self._create_leolani_world_sens(experience)

        # Identity
        leolani = self._generate_leolani(instance_graph) if self.my_uri is None else self.my_uri

        # Leolani talk (includes interaction and perspective graphs)
        interaction_graph, perspective_graph, actor, time, mention, attribution = self._create_leolani_talk_sens(experience, leolani)

        # Interconnections
        instance_graph.add((subject, self.namespaces['GRASP']['denotedIn'], mention))
        instance_graph.add((object, self.namespaces['GRASP']['denotedIn'], mention))

        instance_graph.add((statement, self.namespaces['GRASP']['denotedBy'], mention))
        instance_graph.add((statement, self.namespaces['SEM']['hasActor'], actor))
        instance_graph.add((statement, self.namespaces['SEM']['hasTime'], time))

        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], subject))
        perspective_graph.add((mention, self.namespaces['GRASP']['containsDenotation'], object))
        perspective_graph.add((mention, self.namespaces['GRASP']['denotes'], statement))

        perspective_graph.add((attribution, self.namespaces['GRASP']['isAttributionFor'], mention))


    ######################################### Helpers for conflict processing #########################################
    def _get_conflicts_with_predicate(self, one_to_one_predicate):
        query = """
            PREFIX n2mu: <http://cltl.nl/leolani/n2mu/>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX grasp: <http://groundedannotationframework.org/grasp#>

            select ?sname 
                    (group_concat(?oname ; separator=";") as ?onames) 
                    (group_concat(?authorlabel ; separator=";") as ?authorlabels) 
            where { 
                GRAPH ?g {
                    ?s n2mu:%s ?o .
                    } .
                ?s rdfs:label ?sname .
                ?o rdfs:label ?oname .

                ?g grasp:denotedBy ?m . 
                ?m grasp:wasAttributedTo ?author . 
                ?author rdfs:label ?authorlabel .

            } group by ?sname having (count(distinct ?oname) > 1)
        """ % one_to_one_predicate

        response = self._submit_query(query)
        conflicts = []
        for item in response:
            conflict = {'subject': item['sname']['value'], 'predicate': one_to_one_predicate, 'objects': []}

            values = item['onames']['value'].split(';')
            authors = item['authorlabels']['value'].split(';')

            for val, auth in zip(values, authors):
                option = {'value': val, 'author': auth}
                conflict['objects'].append(option)

            conflicts.append(conflict)

        return conflicts

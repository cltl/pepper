######################################### Helpers for question processing #########################################

def create_query(self, utterance):
    empty = self._rdf_builder.fill_literal('')

    # Query subject
    if utterance.triple.subject_name == empty:
        query = """
                   SELECT distinct ?slabel ?authorlabel ?certaintyValue ?polarityValue ?sentimentValue ?emotionValue ?temporalValue
                           WHERE { 
                               ?s n2mu:%s ?o . 
                               ?s rdfs:label ?slabel . 
                               ?o rdfs:label '%s' .  
                               GRAPH ?g {
                                   ?s n2mu:%s ?o . 
                               } . 
                               ?g gaf:denotedBy ?m . 
                               ?m grasp:wasAttributedTo ?author . 
                               ?author rdfs:label ?authorlabel .

                               ?m grasp:hasAttribution ?att .
                               ?att rdf:value ?certainty .
                               ?certainty rdf:type graspf:CertaintyValue .
                               ?certainty rdfs:label ?certaintyValue .

                               ?att rdf:value ?polarity .
                               ?polarity rdf:type graspf:PolarityValue .
                               ?polarity rdfs:label ?polarityValue .

                               ?att rdf:value ?temporal .
                               ?temporal rdf:type graspf:TemporalValue .
                               ?temporal rdfs:label ?temporalValue .

                               ?att rdf:value ?emotion .
                               ?emotion rdf:type graspe:EmotionValue .
                               ?emotion rdfs:label ?emotionValue .

                               ?att rdf:value ?sentiment .
                               ?sentiment rdf:type grasps:SentimentValue .
                               ?sentiment rdfs:label ?sentimentValue .
                           }
                   """ % (utterance.triple.predicate_name,
                          utterance.triple.complement_name,
                          utterance.triple.predicate_name)

    # Query complement
    elif utterance.triple.complement_name == empty:
        query = """
                   SELECT distinct ?olabel ?authorlabel ?certaintyValue ?polarityValue ?sentimentValue ?emotionValue ?temporalValue
                           WHERE { 
                               ?s n2mu:%s ?o .   
                               ?s rdfs:label '%s' .  
                               ?o rdfs:label ?olabel .  
                               GRAPH ?g {
                                   ?s n2mu:%s ?o . 
                               } . 
                               ?g gaf:denotedBy ?m . 
                               ?m grasp:wasAttributedTo ?author . 
                               ?author rdfs:label ?authorlabel .

                               ?m grasp:hasAttribution ?att .
                               ?att rdf:value ?certainty .
                               ?certainty rdf:type graspf:CertaintyValue .
                               ?certainty rdfs:label ?certaintyValue .

                               ?att rdf:value ?polarity .
                               ?polarity rdf:type graspf:PolarityValue .
                               ?polarity rdfs:label ?polarityValue .

                               ?att rdf:value ?temporal .
                               ?temporal rdf:type graspf:TemporalValue .
                               ?temporal rdfs:label ?temporalValue .

                               ?att rdf:value ?emotion .
                               ?emotion rdf:type graspe:EmotionValue .
                               ?emotion rdfs:label ?emotionValue .

                               ?att rdf:value ?sentiment .
                               ?sentiment rdf:type grasps:SentimentValue .
                               ?sentiment rdfs:label ?sentimentValue .
                           }
                   """ % (utterance.triple.predicate_name,
                          utterance.triple.subject_name,
                          utterance.triple.predicate_name)

    # Query existence
    else:
        query = """
                   SELECT distinct ?authorlabel ?certaintyValue ?polarityValue ?sentimentValue ?emotionValue ?temporalValue
                           WHERE { 
                               ?s n2mu:%s ?o .   
                               ?s rdfs:label '%s' .  
                               ?o rdfs:label '%s' .  
                               GRAPH ?g {
                                   ?s n2mu:%s ?o . 
                               } . 
                               ?g gaf:denotedBy ?m . 
                               ?m grasp:wasAttributedTo ?author . 
                               ?author rdfs:label ?authorlabel .

                               ?m grasp:hasAttribution ?att .
                               ?att rdf:value ?certainty .
                               ?certainty rdf:type graspf:CertaintyValue .
                               ?certainty rdfs:label ?certaintyValue .

                               ?att rdf:value ?polarity .
                               ?polarity rdf:type graspf:PolarityValue .
                               ?polarity rdfs:label ?polarityValue .

                               ?att rdf:value ?temporal .
                               ?temporal rdf:type graspf:TemporalValue .
                               ?temporal rdfs:label ?temporalValue .

                               ?att rdf:value ?emotion .
                               ?emotion rdf:type graspe:EmotionValue .
                               ?emotion rdfs:label ?emotionValue .

                               ?att rdf:value ?sentiment .
                               ?sentiment rdf:type grasps:SentimentValue .
                               ?sentiment rdfs:label ?sentimentValue .
                           }
                   """ % (utterance.triple.predicate_name,
                          utterance.triple.subject_name,
                          utterance.triple.complement_name,
                          utterance.triple.predicate_name)

    query = self.query_prefixes + query

    self._log.info("Triple in question: {}".format(utterance.triple))

    return query

class BDI(object):
    def __init__(self, desires=None, intentions=None):
        """
        Create BDI model.

        Parameters
        ----------
        desires: list
            List of available desires (goals) for this model
        intentions: list
            List of available intentions (actions) for this model

        """

        # Desires represent the overall goal
        if desires is None:
            self._desires = {
                0: 'Hunt for knowledge',
                1: 'Entertain speaker'
            }
        else:
            self._desires = {idx: desire for idx, desire in enumerate(desires)}

        # Intentions are the actions to be taken in the short term
        if intentions is None:
            self._intentions = {
                0: 'Look for people',
                1: 'Recognize person',
                2: 'Greet',
                3: 'Get introduced',
                4: 'Initiate conversation',
                5: 'Listen',
                6: 'Reply',
                7: 'Ask for clarification'
            }
        else:
            self._intentions = {idx: intention for idx, intention in enumerate(intentions)}

        # Beliefs are like a short term memory (running memory)
        # Current state of surroundings
        self.current_beliefs_environment = {}
        # Current internal states
        self.current_beliefs_internal = {}
        # Coming from Knowledge store
        self.current_beliefs_world = {}

        self.current_desire = None
        self.current_intention = None

    @property
    def desires(self):
        """
        Returns
        -------
        desires: dictionary
            Catalogue of possible desires (goals)
        """
        return self._desires

    @property
    def intentions(self):
        """
        Returns
        -------
        intentions: dictionary
            Catalogue of possible intentions (actions)
        """
        return self._intentions

    def next_intention(self):
        """Select next action to perform"""

        if self.current_desire == 0:

            if self.current_intention == 0:
                if self.current_beliefs_environment['person_in_frame']:
                    self.current_intention = 1

            elif self.current_intention == 1:
                if self.current_beliefs_environment['person_known']:
                    self.current_intention = 2
                else:
                    self.current_intention = 3

            elif self.current_intention == 2:
                if self.current_beliefs_environment['person_talking']:
                    self.current_intention = 5
                else:
                    self.current_intention = 4

            elif self.current_intention == 3:
                if self.current_beliefs_environment['person_talking']:
                    self.current_intention = 5
                else:
                    self.current_intention = 4

            elif self.current_intention == 4:
                if self.current_beliefs_environment['person_talking']:
                    self.current_intention = 5

            elif self.current_intention == 5:
                if not self.current_beliefs_environment['person_talking']:
                    if self.current_beliefs_internal['understood']:
                        self.current_intention = 6
                    else:
                        self.current_intention = 7

            elif self.current_intention == 6:
                if self.current_beliefs_environment['person_talking']:
                    self.current_intention = 5

            elif self.current_intention == 7:
                if self.current_beliefs_environment['person_talking']:
                    self.current_intention = 5

        return self.current_intention, self._intentions[self.current_intention]


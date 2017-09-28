import subprocess
import re

class WordNet:
    @staticmethod
    def definition(word):
        """
        Get first definition of word from WordNet

        Parameters
        ----------
        word: str
            Queried word

        Returns
        -------
        definition: str
            First definition of word
        """

        try:
            result = subprocess.check_output(["wn", word, '-over'])
        except subprocess.CalledProcessError as e:
            result = e.output

        definitions = re.findall(r' -- (\(.+?)\n', result)

        return definitions[0]

    @staticmethod
    def definitions(word):
        """
        Get all definitions of word, organised per part of speech

        Parameters
        ----------
        word: str
            Queried word

        Returns
        -------
        definitions: dictionary of lists of string
            Dictionary with parts of speech ('noun', 'verb', etc) as keys and lists of definitions as values
        """

        part_of_speech_definitions = {}

        try: overview = subprocess.check_output(["wn", word, '-over'])
        except subprocess.CalledProcessError as e:
            overview = e.output

        overview = overview.split("Overview of ")[1:]

        for sub_overview in overview:
            part_of_speech = re.findall(r'^(\w+)', sub_overview)[0]
            definitions = re.findall(r' -- (\(.+?)\n', sub_overview)

            part_of_speech_definitions[part_of_speech] = definitions

        return part_of_speech_definitions

import unittest

from shared.string_utils import ProcessingString


class CleaningTest(unittest.TestCase):

    def test_remove_english_stopwords(self):
        ps = ProcessingString('en')
        sentence = "this is a long sentence with a lot of stopwords in it"

        result = ps.remove_stopwords(sentence)

        self.assertNotIn("is", result)
        self.assertNotIn("a", result)
        self.assertNotIn("with", result)

        self.assertIn("sentence", result)
        self.assertIn("long", result)
        self.assertIn("lot", result)
        self.assertIn("stopwords", result)

    def test_remove_french_stopwords(self):
        ps = ProcessingString('fr')
        sentence = "c'est une longue phrase avec beaucoup de mots vides dedans"

        result = ps.remove_stopwords(sentence)

        print(result)

        self.assertNotIn(" une ", result)
        self.assertNotIn(" avec ", result)
        self.assertNotIn(" de ", result)

        self.assertIn("longue", result)
        self.assertIn("phrase", result)
        self.assertIn("beaucoup", result)
        self.assertIn("mots", result)

    def test_stem_word1(self):
        ps = ProcessingString('en')
        word = "running"

        result = ps.stem_word(word)

        self.assertEqual(result, "run")

    def test_stem_word1(self):
        ps = ProcessingString('fr')
        word = "courir"

        result = ps.stem_word(word)

        self.assertEqual(result, "cour")

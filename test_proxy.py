import unittest
from proxy import add_tm


class Test(unittest.TestCase):

    def test_add_tm(self):
        source_code = "<div>Example: normal, dog, kitten,\
                         tag, cheese</div>"
        modified_code = "<div>Example: normal™, dog, kitten™,\
                         tag, cheese™</div>\n"
        self.assertEqual(add_tm(source_code), modified_code)

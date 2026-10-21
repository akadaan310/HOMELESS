import unittest
from verify_numerics import residual_for_rows

class NumericEvidenceTests(unittest.TestCase):
    def test_missing_malformed_and_extra_rows_refuse(self):
        for rows in ([], [['0','0']], [['nan','0','0']], [['0','0','0'],['0','0','0']]):
            self.assertIsNone(residual_for_rows([(0,0,0)],rows))
        self.assertEqual(residual_for_rows([(0,0,0)],[['6378137','0','0']]),0)

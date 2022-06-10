"""
Test the calc function
"""
from django.test import SimpleTestCase

from app.calc import add, subtract


class CalcTests(SimpleTestCase):
    """Test the calc module."""

    def test_add_numbers(self):
        """test adding numbers"""
        result = add(5, 6)

        self.assertEqual(result, 11)

    def test_subtract_numbers(self):
        """test subtracting numbers"""
        result = subtract(5, 6)

        self.assertEqual(result, -1)

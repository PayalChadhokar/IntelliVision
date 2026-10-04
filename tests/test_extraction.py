import unittest

from services.extraction_service import extract_information


class TestExtractionService(unittest.TestCase):

    def test_basic_extraction(self):

        text = """
        My name is Rahul Sharma.
        Yesterday at 8 PM my mobile phone was stolen
        from Central Market, Nagpur.
        The phone is a Samsung Galaxy and cost Rs. 25000.
        """

        result = extract_information(text)

        self.assertIsInstance(
            result,
            dict
        )


    def test_empty_text(self):

        result = extract_information("")

        self.assertIsInstance(
            result,
            dict
        )


if __name__ == "__main__":
    unittest.main()
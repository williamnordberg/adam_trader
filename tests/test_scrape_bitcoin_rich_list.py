import unittest
import os
from bs4_scraper import scrape_bitcoin_rich_list, OUTPUT_FILE


class TestScrapeBitcoinRichList(unittest.TestCase):
    def test_scrape_bitcoin_rich_list(self):

        # Ensure the output file does not exist before running the function
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)

        # Call the scrape_bitcoin_rich_list function
        scrape_bitcoin_rich_list()

        # Check if the output file was created
        self.assertTrue(os.path.exists(OUTPUT_FILE), "The output CSV file was not created.")

        # Clean up: Remove the output file after the test
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)


if __name__ == "__main__":
    unittest.main()

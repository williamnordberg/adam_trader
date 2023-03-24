import unittest
from unittest.mock import MagicMock
import pandas as pd

from scrapy.http import HtmlResponse
from spider import BitcoinRichListSpider


class TestBitcoinRichListSpider(unittest.TestCase):

    def setUp(self):
        self.spider = BitcoinRichListSpider()

    def test_init(self):
        self.assertIsInstance(self.spider.df, pd.DataFrame)
        self.assertEqual(self.spider.df.columns.tolist(), ["address"])

    def test_parse(self):
        # Mock the response object with sample HTML
        response = HtmlResponse(url="http://example.com", body="""
        <table>
            <tr>
                <td>1</td>
                <td><a href="#">address1</a></td>
            </tr>
            <tr>
                <td>2</td>
                <td><a href="#">address2</a></td>
            </tr>
        </table>
        """.encode('utf-8'), encoding='utf-8')  # Add encoding here

        # Spy on the spider's 'to_csv' method to avoid writing to a real file during tests
        self.spider.df.to_csv = MagicMock()

        # Call the parse method
        self.spider.parse(response)

        # Check if the parse method has appended the correct data
        self.assertEqual(len(self.spider.df), 2)

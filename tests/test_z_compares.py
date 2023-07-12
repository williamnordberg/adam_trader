import unittest
from z_compares import compare_macro_m_to_m, compare_order_volume, compare_technical,\
    compare_google_reddit_youtube, compare_news, compare_predicted_price


class TestCompares(unittest.TestCase):

    def test_compare_predicted_price(self):
        self.assertEqual(compare_predicted_price(101, 100), (6, 4))

        self.assertEqual(compare_predicted_price(98, 100), (3, 7))

        self.assertEqual(compare_predicted_price(100, 100), (0.0, 0.0))

    def test_compare_macro_m_to_m(self):
        self.assertEqual(compare_macro_m_to_m(-0.76), (1.0, 0.0))
        self.assertEqual(compare_macro_m_to_m(-0.51), (0.85, 0.15))

    def test_compare_order_volume(self):
        self.assertEqual(compare_order_volume(0.57, 0), (0.7, 0.3))

        self.assertEqual(compare_order_volume(0, 0.57), (0.3, 0.7))

        self.assertEqual(compare_order_volume(0, 0.60), (0.2, 0.8))

        self.assertEqual(compare_order_volume(0, 0.63), (0.1, 0.9))

        self.assertEqual(compare_order_volume(0, 0.57), (0.3, 0.7))

        self.assertEqual(compare_order_volume(0.57, 0), (0.7, 0.3))

        self.assertEqual(compare_order_volume(0.60, 0), (0.8, 0.2))

        self.assertEqual(compare_order_volume(0.62, 0), (0.9, 0.1))

    def test_compare_technical(self):
        # testing with known inputs
        self.assertEqual(compare_technical('up', True, True), (1, 0))
        # testing with reversed inputs
        self.assertEqual(compare_technical('down', False, False), (0, 1))

    def test_compare_google_reddit_youtube(self):
        self.assertEqual(compare_google_reddit_youtube(100, 109), (0.0, 0.0))
        self.assertEqual(compare_google_reddit_youtube(109, 100), (0.0, 0.0))

        self.assertEqual(compare_google_reddit_youtube(110, 100), (0.6, 0.4))
        self.assertEqual(compare_google_reddit_youtube(100, 110), (0.4, 0.6))

        self.assertEqual(compare_google_reddit_youtube(124, 100), (0.85, 0.15))
        self.assertEqual(compare_google_reddit_youtube(100, 124), (0.15, 0.85))

        self.assertEqual(compare_google_reddit_youtube(115, 100), (0.75, 0.25))
        self.assertEqual(compare_google_reddit_youtube(100, 115), (0.25, 0.75))

    def test_compare_news(self):
        self.assertEqual(compare_news(1, -1, 10000, 0), (1, 0.0))
        self.assertEqual(compare_news(-1, 1.04, 0, 10000), (0.0, 1))

        self.assertEqual(compare_news(1, -1, 10000, 0), (1, 0.0))
        self.assertEqual(compare_news(-1, 1.04, 0, 10000), (0.0, 1))

        self.assertEqual(compare_news(1, 1, 0, 10000), (0.2, 0.8))
        self.assertEqual(compare_news(0, -1, 10000, 0), (0.8, 0.2))


if __name__ == '__main__':
    unittest.main()

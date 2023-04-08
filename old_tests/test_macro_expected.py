from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock, patch
import macro_analyser as me


class TestMacroExpected(unittest.TestCase):

    @patch("macro_expected.webdriver.Remote")
    def test_get_macro_expected_and_real_compare(self, mock_remote):
        """
              Test if the get_macro_expected_and_real_compare function returns the expected results.
        """
        # Set up the mock BeautifulSoup object for testing
        soup_mock = MagicMock()
        table_mock = MagicMock()
        soup_mock.find.return_value = table_mock

        # Mock the actual and forecast values for testing
        actual_values = ["1.0%", "4.0%", "6.0%"]
        forecast_values = ["1.1%", "4.1%", "6.1%"]

        # Mock the event rows
        event_rows = []
        for actual, forecast in zip(actual_values, forecast_values):
            row_mock = MagicMock()
            actual_cell_mock = MagicMock()
            forecast_cell_mock = MagicMock()
            actual_cell_mock.text.strip.return_value = actual
            forecast_cell_mock.string = forecast

            # Set the side_effect for row_mock.find
            row_mock.find.side_effect = lambda *args, **kwargs: actual_cell_mock \
                if "actual" in kwargs.get("class_",
                                          "") else forecast_cell_mock
            event_rows.append(row_mock)

        table_mock.find_all.return_value = event_rows

        with patch("macro_expected.BeautifulSoup", return_value=soup_mock):
            results = me.macro_sentiment()

        # Check if the function returns the expected results
        self.assertEqual(results, (False, False, False,
                                   {'CPI m/m': None, 'CPI y/y': None, 'Core CPI m/m': None, 'Core PPI m/m': None,
                                    'Federal Funds Rate': None, 'PPI m/m': None}))

    @patch("macro_expected.datetime")
    def test_print_upcoming_events(self, mock_datetime):
        """
              Test if print_upcoming_events function logs the expected events.
        """
        # Mock the current date and time for testing
        current_datetime = datetime(2023, 3, 23, 0, 0, 0)
        mock_datetime.utcnow.return_value = current_datetime

        # Set up a sample events_date_dict for testing
        events_date_dict = {
            "Event 1": current_datetime + timedelta(days=1),
            "Event 2": current_datetime + timedelta(days=2),
            "Event 3": current_datetime + timedelta(days=3),
            "Event 4": None
        }

        with self.assertLogs(level="INFO") as log:
            me.print_upcoming_events(events_date_dict)

        # Check if the function logs the expected events
        self.assertIn("INFO:root:Upcoming event: Event 1 x, 1 day(s), 0 hour(s),"
                      " 0 min(s) remaining", log.output)
        self.assertIn("INFO:root:Upcoming event: Event 2 x, 2 day(s), 0 hour(s), "
                      "0 min(s) remaining", log.output)
        self.assertNotIn("INFO:root:Upcoming event: Event 3 x, 3 day(s), 0 hour(s),"
                         " 0 min(s) remaining", log.output)
        self.assertNotIn("INFO:root:Upcoming event: Event 4 x", log.output)


if __name__ == "__main__":
    unittest.main()

import unittest
from news_compare_polarity import compare_polarity


class TestNewsComparePolarity(unittest.TestCase):
    def test_compare_polarity_case1(self):
        # Define the test inputs and expected output
        input1 = 2
        input2 = 1
        input3 = 2
        input4 = 2
        expected_output1 = 1
        expected_output2 = 0

        # Call the compare_polarity function with the test inputs
        output1, output2 = compare_polarity(input1, input2, input3, input4)

        # Check if the function's output matches the expected output
        self.assertEqual(output1, expected_output1, "Output 1 is not as expected.")
        self.assertEqual(output2, expected_output2, "Output 2 is not as expected.")

    def test_compare_polarity_case2(self):
        # Define the test inputs and expected output
        input1 = 1
        input2 = 2
        input3 = 2
        input4 = 1
        expected_output1 = 0
        expected_output2 = 1

        # Call the compare_polarity function with the test inputs
        output1, output2 = compare_polarity(input1, input2, input3, input4)

        # Check if the function's output matches the expected output
        self.assertEqual(output1, expected_output1, "Output 1 is not as expected.")
        self.assertEqual(output2, expected_output2, "Output 2 is not as expected.")


if __name__ == "__main__":
    unittest.main()

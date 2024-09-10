#unittest find next highest RRT
import unittest
import pandas as pd

# Add the directory containing 'utils' to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

# Now you can import 'utils'
import utils

class TestRRT(unittest.TestCase):
    def test_find_next_least_rrt(self):
        # Create sample data
        data = pd.DataFrame({
            'Vial': ['A', 'A', 'B', 'B'],
            'RRT': [0.5, 1.0, 0.75, 1.0]
        })
        vial = 'A'
        rrt = 1.0

        # Call the function
        result = utils.find_next_least_rrt(data, vial, rrt)

        # Inspect the data types of the result DataFrame
        print(result.dtypes)

        # Assert the expected output with matching data types
        expected_result = pd.DataFrame({
            'Vial': pd.Series(['A'], dtype=result['Vial'].dtype),
            'RRT': pd.Series([0.5], dtype=result['RRT'].dtype)
        })

        pd.testing.assert_frame_equal(result, expected_result)
    def test_find_next_highest_rrt(self):
        # Create sample data
        data = pd.DataFrame({
            'Vial': ['A', 'A', 'B', 'B'],
            'RRT': [0.5, 1.0, 0.75, 1.0]
        })
        vial = 'A'
        rrt = 0.5

        # Call the function
        result = utils.find_next_highest_rrt(data, vial, rrt)

        # Inspect the data types of the result DataFrame
        print(result.dtypes)

        # Assert the expected output with matching data types
        expected_result = pd.DataFrame({
            'Vial': pd.Series(['A'], dtype=result['Vial'].dtype),
            'RRT': pd.Series([1.0], dtype=result['RRT'].dtype)
        })
        pd.testing.assert_frame_equal(result, expected_result)
        
    def test_group_peaksandRRTs(self):
        # Create sample data
        data = pd.DataFrame({
            'RRT': [0.5, 0.5, 0.75, 0.75, 1.0, 1.0],
            'peakCount': [2, 2, 1, 1, 3, 3],
            'AreaRatio': [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]
        })

        # Call the function
        result = utils.group_peaksandRRTs(data)

        # Assert the expected output
        expected_result = pd.DataFrame({
            'RRT': [0.5, 0.75, 1.0],
            'peakCount': [2, 2, 2],
            'AreaRatio Sum': [0.5, 0.9, 1.3],
            'shift global RRT': ['None', 'None', 'None']
        })

        pd.testing.assert_frame_equal(result, expected_result)
if __name__ == '__main__':
    unittest.main()

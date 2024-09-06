import unittest
import pandas as pd

# Add the directory containing 'utils' to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

# Now you can import 'utils'
import utils

class TestUtils(unittest.TestCase):
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

        # Assert the expected output
        expected_result = pd.DataFrame({
            'Vial': ['A'],
            'RRT': [0.5]
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

        # Assert the expected output
        expected_result = pd.DataFrame({
            'Vial': ['A'],
            'RRT': [1.0]
        })

        pd.testing.assert_frame_equal(result, expected_result)
    def test_process_uploaded_file(self):
        # Create a sample Excel file
        data = pd.DataFrame({
            'Vial': ['1:A,1', '1:A,1', '1:B,1', '1:B,1'],
            'Retention Time': [1.0, 2.0, 3.0, 4.0],
            'Area': [100, 200, 300, 400]
        })
        file_path = 'sample_file.xlsx'
        data.to_excel(file_path, index=False)

        # Call the function
        processed_data, maxarea, df_vial_counts = utils.process_uploaded_file(file_path)

        # Assert the expected output
        expected_processed_data = pd.DataFrame({
            'Vial': ['1:A,1', '1:A,1', '1:B,1', '1:B,1'],
            'Retention Time': [1.0, 2.0, 3.0, 4.0],
            'Area': [100, 200, 300, 400]
        })
        expected_maxarea = pd.DataFrame({
            'Vial': ['1:B,1', '1:B,1','1:A,1', '1:A,1', ],
            'Area': [400, 300, 200, 100],
            'Area Sum': [300, 700],
            'Area Ratio': [33.33, 57.14],
            'Retention Time': [2.0, 4.0],
            'peakCount': [2, 2],
            'Plate': [1, 1],
            'Vial_Well': ['A,1', 'B,1']
        })
        expected_df_vial_counts = pd.DataFrame({
            'Vial': ['A', 'B'],
            'peakCount': [2, 2]
        })

        pd.testing.assert_frame_equal(processed_data, expected_processed_data)
        pd.testing.assert_frame_equal(maxarea, expected_maxarea)
        pd.testing.assert_frame_equal(df_vial_counts, expected_df_vial_counts)

        # Clean up the sample file
        os.remove(file_path)
if __name__ == '__main__':
    unittest.main()
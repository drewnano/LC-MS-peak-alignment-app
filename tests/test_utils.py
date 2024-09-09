import unittest
import pandas as pd

# Add the directory containing 'utils' to the Python path
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

# Now you can import 'utils'
import utils

class TestUtils(unittest.TestCase):
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
        processed_data, maxarea = utils.process_uploaded_file(file_path)

        # Assert the expected output
        expected_processed_data = pd.DataFrame({
            'Vial': ['1:A,1', '1:A,1', '1:B,1', '1:B,1'],
            'Retention Time': [1.0, 2.0, 3.0, 4.0],
            'Area': [100, 200, 300, 400]
        })
        expected_processed_data['Retention Time'] = expected_processed_data['Retention Time'].astype(processed_data['Retention Time'].dtype)
        expected_maxarea = pd.DataFrame({
            'Vial': ['1:A,1', '1:B,1'],
            'Area': [200, 400],
            'Area Sum': [300, 700],
            'Area Ratio': [2/3, 4/7],
            'Retention Time': [2.0, 4.0],
            'peakCount': [2, 2],
            'Plate': [1, 1],
            'Vial_Well': ['A,1', 'B,1']
        })
        expected_maxarea['Retention Time'] = expected_maxarea['Retention Time'].astype(maxarea['Retention Time'].dtype)
        expected_maxarea['Plate'] = expected_maxarea['Plate'].astype(maxarea['Plate'].dtype)
        expected_df_vial_counts = pd.DataFrame({
            'Vial': ['1:A,1', '1:B,1'],
            'peakCount': [2, 2]
        })

        pd.testing.assert_frame_equal(processed_data, expected_processed_data)
        pd.testing.assert_frame_equal(maxarea, expected_maxarea)

        # Clean up the sample file
        os.remove(file_path)
if __name__ == '__main__':
    class TestUtils(unittest.TestCase):
        def test_shift_rrt(self):
            # Create sample data
            data = pd.DataFrame({
                'SampleName': ['Sample1', 'Sample1', 'Sample2', 'Sample2'],
                'Vial': ['A', 'A', 'B', 'B'],
                'RRT': [0.5, 1.0, 0.75, 1.0],
                'AreaRatio': [0.2, 0.3, 0.4, 0.5]
            })

            # Call the function
            selected_rows_df, pivoted_df = shift_rrt(data)

            # Assert the expected output
            expected_selected_rows_df = pd.DataFrame({
                'SampleName': ['Sample1', 'Sample1', 'Sample2', 'Sample2'],
                'Vial': ['A', 'A', 'B', 'B'],
                'RRT': [0.5, 1.0, 0.75, 1.0],
                'AreaRatio': [0.2, 0.3, 0.4, 0.5]
            })

            expected_pivoted_df = pd.DataFrame({
                'SampleName': ['Sample1', 'Sample2'],
                'Vial': ['A', 'B'],
                0.5: [0.2, 0],
                1.0: [0.3, 0.9],
                0.75: [0, 0.4]
            })

            pd.testing.assert_frame_equal(selected_rows_df, expected_selected_rows_df)
            pd.testing.assert_frame_equal(pivoted_df, expected_pivoted_df)

    if __name__ == '__main__':
        unittest.main()
    unittest.main()
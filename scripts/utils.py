import pandas as pd
import streamlit as st

def process_uploaded_file(uploaded_file):
    """Process the uploaded Excel file and pre-process data."""
    if uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
    elif uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        st.error("Unsupported file format")
        return None, None
    df_vial_counts = data.groupby(['Vial']).size().reset_index(name='peakCount')
    maxarea = data.groupby(['Vial'])['Area'].max().reset_index()
    areasum = data.groupby(['Vial'])['Area'].sum().reset_index(name='Sum of Area')
    maxarea['Area Sum'] = areasum['Sum of Area']
    maxarea['Area Ratio'] = (maxarea['Area'] / maxarea['Area Sum'])
    RTmax = (data.sort_values(['Vial', 'Area'], ascending=[True, False])
             .drop_duplicates(['Vial']).reset_index(drop=True)
            )
    maxarea = pd.merge(maxarea, RTmax, how='left', on=['Vial', 'Area'])
    maxarea = pd.merge(maxarea, df_vial_counts, how='left', on='Vial')
    maxarea[['Plate', 'Vial_Well']] = maxarea['Vial'].str.split(':', expand=True)
    return data, maxarea

def calculate_rrt(data, maxarea):
    """Calculate RRT and Area Ratio for the peaks."""
    data['RRT'] = data.apply(lambda row: row['Retention Time'] / 
                             maxarea[maxarea['Vial'] == row['Vial']]['Retention Time'].values[0], axis=1)
    data['RRT'] = data['RRT'].round(2)
    data['AreaRatio'] = data.apply(lambda row: row['Area'] / 
                                   maxarea[maxarea['Vial'] == row['Vial']]['Area'].values[0], axis=1)
    return data

def find_next_least_rrt(data, vial, rrt):
    """Filter the DataFrame to find the next least RRT for the given vial"""
    subset_df = data[(data['Vial'] == vial) & (data['RRT'] < rrt)]
    if subset_df.empty:
        return pd.DataFrame(columns=data.columns)  # Return an empty DataFrame with the same columns
    next_row = subset_df.loc[subset_df['RRT'].idxmax()]
    # Convert the Series to a DataFrame
    result_df = next_row.to_frame().T
    # Ensure the correct data types
    result_df = result_df.astype(data.dtypes.to_dict())
    return result_df

def find_next_highest_rrt(df, vial, rrt):
    """Filter the DataFrame to find the next highest RRT for the given vial"""
    subset_df = df[(df['Vial'] == vial) & (df['RRT'] > rrt)]
    if subset_df.empty:
        return pd.DataFrame(columns=df.columns)  # Return an empty DataFrame with the same columns
    next_row = subset_df.loc[subset_df['RRT'].idxmin()]
    # Convert the Series to a DataFrame
    result_df = next_row.to_frame().T
    # Ensure the correct data types
    result_df = result_df.astype(df.dtypes.to_dict())
    return result_df

def group_peaksandRRTs(data):
    """group peaks and RRTs so we may prepare to shift them"""
    # Group and calculate peakCount and AreaRatio Sum for each RRT
    df_RRT = data.groupby(['RRT']).size().reset_index(name='peakCount')
    df_RRT_area_ratio = data.groupby(['RRT'])['AreaRatio'].sum().reset_index(name='AreaRatio Sum')
    df_RRT = pd.merge(df_RRT, df_RRT_area_ratio, on='RRT')

    # Add a column 'shift global RRT' for shift action dropdowns
    df_RRT['shift global RRT'] = 'None'
    return df_RRT

def shift_rrt(data):
    """Handle RRT shifting and return updated data for display."""
    df_RRT = group_peaksandRRTs(data)
    # Display the df_RRT with the shift actions in the frontend
    st.write("Shift Actions for each global RRT:")
    st.dataframe(df_RRT)  # Display df_RRT on the frontend

    # Add a list to store user-selected actions
    shift_actions = []

    st.write("Select global RRT values for merging peaks")

    # For each row, create a selectbox for the action
    for index, row in df_RRT.iterrows():
        # Add a dropdown for each row in the 'shift global RRT' column
        shiftaction = st.selectbox(
            f"Action for RRT {row['RRT']}:",
            options=['None', '< shift to left', '> shift to right'],
            index=0,  # 'None' is the default option
            key=f"shift_action_{index}"  # Unique key for each dropdown
        )
        # Store the selected action
        shift_actions.append(shiftaction)

    # Assign the actions back to the DataFrame
    df_RRT['shift global RRT'] = shift_actions

    """Process the RRT shifting based on the actions in df_RRT and return updated data."""
    selected_rows_df = pd.DataFrame(columns=data.columns)
    
    # Iterate through each row in the dataframe 'data'
    for index, data_row in data.iterrows():
        # Check if the 'RRT' in 'data_row' exists in 'df_RRT'
        matching_rrt_row = df_RRT[df_RRT['RRT'] == data_row['RRT']]

        if not matching_rrt_row.empty:
            # Get the 'shiftaction' for the matching RRT row from df_RRT
            shiftaction = matching_rrt_row['shift global RRT'].values[0]

            # If no shift action, simply add the row to 'selected_rows_df'
            if shiftaction == 'None':
                selected_rows_df = pd.concat([selected_rows_df, pd.DataFrame([data_row])], ignore_index=True)

            # If "< shift to left", find next least RRT and merge the rows
            elif shiftaction == '< shift to left':
                next_row = find_next_least_rrt(data, data_row['Vial'], data_row['RRT'])
                if next_row is not None:
                    modified_row = next_row.copy()
                    modified_row['SampleName'] = data_row['SampleName']
                    modified_row['Vial'] = data_row['Vial']
                    modified_row['RRT'] = next_row['RRT']
                    modified_row['AreaRatio'] = data_row['AreaRatio'] + next_row['AreaRatio']

                    # Ensure 'modified_row' is a DataFrame before concatenation
                    if isinstance(modified_row, pd.Series):
                        modified_row = modified_row.to_frame().T

                    # Concatenate the modified row to the selected rows dataframe
                    selected_rows_df = pd.concat([selected_rows_df, modified_row], ignore_index=True)

            # If "> shift to right", find next highest RRT and merge the rows
            elif shiftaction == '> shift to right':
                next_row = find_next_highest_rrt(data, data_row['Vial'], data_row['RRT'])
                if next_row is not None:
                    modified_row = next_row.copy()
                    modified_row['SampleName'] = data_row['SampleName']
                    modified_row['Vial'] = data_row['Vial']
                    modified_row['RRT'] = next_row['RRT']
                    modified_row['AreaRatio'] = data_row['AreaRatio'] + next_row['AreaRatio']

                    # Ensure 'modified_row' is a DataFrame before concatenation
                    if isinstance(modified_row, pd.Series):
                        modified_row = modified_row.to_frame().T

                    # Concatenate the modified row to the selected rows dataframe
                    selected_rows_df = pd.concat([selected_rows_df, modified_row], ignore_index=True)
        else:
            # If no matching RRT in df_RRT, just append the row to 'selected_rows_df'
            selected_rows_df = pd.concat([selected_rows_df, pd.DataFrame([data_row])], ignore_index=True)

    # Pivot the selected rows for display
    pivoted_df = selected_rows_df.pivot_table(index=['SampleName', 'Vial'], columns='RRT', values='AreaRatio', fill_value=0)
    return selected_rows_df, pivoted_df
    
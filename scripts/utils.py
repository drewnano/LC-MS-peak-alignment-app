import pandas as pd
import streamlit as st

def process_uploaded_file(uploaded_file):
    """Process the uploaded Excel file and pre-process data."""
    data = pd.read_excel(uploaded_file)
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

import pandas as pd

def find_next_least_rrt(data, vial, rrt):
    """Filter the DataFrame to find the next least RRT for the given vial"""
    subset_df = data[(data['Vial'] == vial) & (data['RRT'] < rrt)]
    if subset_df.empty:
        return pd.DataFrame(columns=data.columns)  # Return an empty DataFrame with the same columns
    next_row = subset_df.loc[subset_df['RRT'].idxmin()]
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

def shift_rrt(data):
    """Handle RRT shifting and return updated data for display."""
    selected_rows_df = pd.DataFrame(columns=data.columns)
    df_RRT = data.groupby(['RRT']).size().reset_index(name='peakCount')
    df_RRT_area_ratio = data.groupby(['RRT'])['AreaRatio'].sum().reset_index(name='AreaRatio Sum')
    df_RRT = pd.merge(df_RRT, df_RRT_area_ratio, on='RRT')
    df_RRT['shift global RRT'] = 'None'
    
    st.write("Select global RRT values for merging peaks")

    for index, row in df_RRT.iterrows():
        shiftaction = st.selectbox(
            f"Action for {row['shift global RRT']}:",
            options=['None', '< shift to left', '> shift to right'],
            index=0,
            key=index 
        )

        if shiftaction == 'None':
            selected_rows_df = selected_rows_df.append(data[data['RRT'] == row['RRT']], ignore_index=True)

        if shiftaction == '< shift to left':
            next_row = find_next_least_rrt(data, row['Vial'], row['RRT'])
            if next_row is not None:
                next_row['SampleName'] = row['SampleName']
                next_row['Vial'] = row['Vial']
                next_row['RRT'] = next_row['RRT']
                next_row['AreaRatio'] = row['AreaRatio'] + next_row['AreaRatio']
                selected_rows_df = selected_rows_df.append(next_row, ignore_index=True)
        
        elif shiftaction == '> shift to right':
            next_row = find_next_highest_rrt(data, row['Vial'], row['RRT'])
            if next_row is not None:
                next_row['SampleName'] = row['SampleName']
                next_row['Vial'] = row['Vial']
                next_row['RRT'] = next_row['RRT']
                next_row['AreaRatio'] = row['AreaRatio'] + next_row['AreaRatio']
                selected_rows_df = selected_rows_df.append(next_row, ignore_index=True)

    pivoted_df = selected_rows_df.pivot_table(index=['SampleName', 'Vial'], columns='RRT', values='AreaRatio', fill_value=0)
    return selected_rows_df, pivoted_df
# %% [markdown]
# MS peak align based on bioAssay peak alignment for excipient screening
# see nb-dejejord-5094579-001

# %%
#Loading Modules
import pandas as pd #handling of csv files and dataframes
import numpy as np
import ipywidgets as widgets
from IPython.display import display
import streamlit as st


# %%


# %%
#loading data 
data = pd.read_excel('./exampledata/Week2_Trimmed.xlsx')


# %% [markdown]
# pre-processing and qc steps
# return parent peak retention time median, min RT, max RT, enter global parent peak RT (optional)
# parent API peak cutoff
# 

# %%
df_vial_counts = data.groupby(['Vial']).size().reset_index(name='peakCount')
maxarea = data.groupby(['Vial'])['Area'].max().reset_index()
areasum = data.groupby(['Vial'])['Area'].sum().reset_index(name='Sum of Area')
maxarea['Area Sum'] = areasum['Sum of Area']
maxarea['Area Ratio'] = maxarea['Area']/ maxarea['Area Sum']*100
RTmax= (data.sort_values(['Vial', 'Area'], ascending=[True, False])
             .drop_duplicates(['Vial']).reset_index(drop=True)
          )
maxarea = pd.merge(maxarea,RTmax,how = 'left', on = ['Vial', 'Area'])
maxarea = pd.merge(maxarea,df_vial_counts, how = 'left', on = 'Vial')
maxarea[['Plate','Vial_Well']] = maxarea['Vial'].str.split(':',expand=True)

# %%
print(data.head(10))

# %%

median_retention_time = maxarea['Retention Time'].median()
min_retention_time = maxarea['Retention Time'].min()
max_retention_time = maxarea['Retention Time'].max()
#print median, min and max retention time
print('Median retention time:', median_retention_time)
print('Minimum retention time:', min_retention_time)
print('Maximum retention time:', max_retention_time)

# %% [markdown]
# calculate RRT values, count of vial peaks, sum of AreaRatio, Assign noise, Shift global RRT option to merge

# %%
#calculate relative rention time 'RRT' of all of the peaks
data['RRT'] = data.apply(lambda row: row['Retention Time'] / maxarea[maxarea['Vial'] == row['Vial']]['Retention Time'].values[0], axis=1)
data['RRT'] = data['RRT'].round(2)
#calculate Area ratio of all of the peaks
data['AreaRatio'] = data.apply(lambda row: row['Area']/ maxarea[maxarea['Vial'] == row['Vial']]['Area'].values[0], axis=1)
#count number of rows with each RRT value
df_RRT_counts = data.groupby(['RRT']).size().reset_index(name='peakCount')
#find the RRT value with the highest number of peaks
max_RRT = df_RRT_counts[df_RRT_counts['peakCount'] == df_RRT_counts['peakCount'].max()]['RRT'].values[0]
#return the sum of the area ratio values for each RRT value
df_RRT_area_ratio = data.groupby(['RRT'])['AreaRatio'].sum().reset_index(name='AreaRatio Sum')
df_RRT = pd.merge(df_RRT_counts, df_RRT_area_ratio, on='RRT')
print(df_RRT.head(10))

# %%
#subset data to only the rows SampleName, Vial, RRT, and AreaRatio
data = data[['SampleName', 'Vial', 'RRT', 'AreaRatio']]

# %% [markdown]
# After you choose which peaks to shift, show what you are shifting in a table essentially

# %%
selected_rows_df = pd.DataFrame(columns=data.columns)
df_RRT['shift global RRT'] = ''
# Streamlit title
st.title("Select global RRT values for merging peaks")

# Function to find the row with the next least 'RRT' value for the same 'vial'
def find_next_least_rrt(df, vial, rrt):
    subset_df = df[(df['Vial'] == vial) & (df['RRT'] > rrt)]
    if not subset_df.empty:
        next_row = subset_df.loc[subset_df['RRT'].idxmin()]
        return next_row
    else:
        return None

# Function to find the row with the next highest 'RRT' value for the same 'vial'
def find_next_highest_rrt(df, vial, rrt):
    subset_df = df[(df['Vial'] == vial) & (df['RRT'] < rrt)]
    if not subset_df.empty:
        next_row = subset_df.loc[subset_df['RRT'].idxmax()]
        return next_row
    else:
        return None

# Display dropdown menus for each row
st.write("Select an action for each row:")
for index, row in df_RRT.iterrows():
    # Dropdown for selecting an action with 'None' as the default option
    shiftaction = st.selectbox(
        f"Action for {row['shift global RRT']}:",
        options=['', '< shift to left', '> shift to right'],
        index=0,  # 'None' is the default option
        key=index  # Use the row index as the key for unique identification
    )

    # if 'None' is selected, add the rows from each vial with this RRT value to the 'selected_rows_df'
    if shiftaction == 'None':
        selected_rows_df = selected_rows_df.append(data[data['RRT'] == row['RRT']], ignore_index=True)

    
    # If "< shift to left" is selected, find the next lowest RRT row and combine their arearatios and add to 'selected_rows_df
    if shiftaction == '< shift to left':
        next_row = find_next_least_rrt(data, row['Vial'], row['RRT'])
        if next_row is not None:
            next_row['SampleName'] = row['SampleName']
            next_row['Vial'] = row['Vial']
            next_row['RRT'] = next_row['RRT']
            next_row['AreaRatio'] = row['AreaRatio'] + next_row['AreaRatio']
            selected_rows_df = selected_rows_df.append(next_row, ignore_index=True)
    
    # If "> shift to right" is selected, find the next highest RRT row and combine their arearatios and add to `selected_rows_df`
    elif shiftaction == '> shift to right':
        next_row = find_next_highest_rrt(data, row['Vial'], row['RRT'])
        if next_row is not None:
            next_row['SampleName'] = row['SampleName']
            next_row['Vial'] = row['Vial']
            next_row['RRT'] = next_row['RRT']
            next_row['AreaRatio'] = row['AreaRatio'] + next_row['AreaRatio']
            selected_rows_df = selected_rows_df.append(next_row, ignore_index=True)
# Display the updated DataFrame
st.write("Selected Rows DataFrame:")
st.write(selected_rows_df)


# %%
print(selected_rows_df.head(10))



# Loading Modules
import pandas as pd
import numpy as np
import streamlit as st
from utils import process_uploaded_file, calculate_rrt, shift_rrt

# Set Streamlit configuration
st.set_page_config(page_title="Peak Alignment App", layout="wide")
st.title("LC Peak Alignment Tool")
st.markdown("Hackathon Team Members: Andrew Sinegra, Stephanie Mozley, Kevin Wang, Kabir Dhingra, and David Gray")
st.markdown("---")

# File uploader widget
uploaded_file = st.file_uploader("Upload an excel file of the peaks", type=["xlsx"])

# Check if a file has been uploaded
if uploaded_file is not None:
    # Process the uploaded file
    data, maxarea = process_uploaded_file(uploaded_file)
    
    # Display the uploaded DataFrame
    st.write("Uploaded DataFrame:")
    st.write(data)
    
    # Calculate RRT values and other metrics
    data = calculate_rrt(data, maxarea)
    
    # Shift global RRT values for merging peaks
    selected_rows_df, pivoted_df = shift_rrt(data)
    
    # Display the updated DataFrame
    st.write("Selected Rows DataFrame:")
    st.write(selected_rows_df)
    
    # Convert the DataFrame to a CSV format
    csv = pivoted_df.to_csv(index=False)
    st.download_button(
        label="Download Output as CSV",
        data=csv,
        file_name='selected_rows.csv',
        mime='text/csv',
    )
    
    # Print for debugging
    print(pivoted_df.head(10))

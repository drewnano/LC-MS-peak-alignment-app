# Loading Modules
import pandas as pd
import numpy as np
import streamlit as st
from utils import process_uploaded_file, calculate_rrt, shift_rrt
from PIL import Image
import base64

# Set Streamlit configuration
st.set_page_config(page_title="Peak Alignment App", layout="wide")

# Load the image and convert to base64 for embedding in HTML
def get_base64_image(image_path):
    with open(image_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode()
    return encoded_image

# Convert the image to base64
image_base64 = get_base64_image("02852_Merck_Logo_Horizontal_Teal&White_RGB.png")

# Add CSS to center the image
st.markdown(
    f"""
    <style>
    .centered-image {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 300px;  /* Adjust the width as necessary */
    }}
    </style>
    <img src="data:image/png;base64,{image_base64}" class="centered-image">
    """, unsafe_allow_html=True
)

st.title("LC Peak Alignment Tool")
st.markdown("DSCS Hackathon Team 3: Kabir Dhingra, David Gray, Stephanie Mozley, Andrew Sinegra, and Kevin Wang")
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
    st.write("Processed DataFrame:")
    st.write(selected_rows_df)
    
    # Convert the DataFrame to a CSV format
    csv = selected_rows_df.to_csv(index=True, header=True)
    file_name = uploaded_file.name.replace(".xlsx", "") + "_selectedrowswRRT.csv"
    st.download_button(
        label="Download processed output as CSV",
        data=csv,
        file_name=file_name,
        mime='text/csv',
    )
    st.write("Pivoted DataFrame:")
    st.dataframe(pivoted_df)

    csv2 = pivoted_df.to_csv(index=True, header=True)
    pivoted_filename = uploaded_file.name.replace(".xlsx", "") + "_RRTspivoted.csv"
    st.download_button(
        label="Download pivoted output as CSV",
        data=csv2,
        file_name=pivoted_filename,
        mime='text/csv',
    )
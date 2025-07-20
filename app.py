import streamlit as st
import pandas as pd

st.title("HealthKart Influencer Campaign Dashboard")
st.write("Welcome! Upload your campaign Excel file below.")

# File uploader
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

# Process file if uploaded
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write("Preview of uploaded file:")
    st.dataframe(df)

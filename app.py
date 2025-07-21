import streamlit as st
import pandas as pd

st.set_page_config(page_title="Influencer Campaign Dashboard", layout="wide")
st.title("📊 Influencer Campaign Dashboard")

# --- Upload Section ---
st.sidebar.header("Upload Excel Files")
uploaded_files = st.sidebar.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

# --- Combine Data ---
if uploaded_files:
    df_list = []
    for file in uploaded_files:
        try:
            df = pd.read_excel(file)
            df_list.append(df)
        except Exception as e:
            st.error(f"Error reading {file.name}: {e}")

    if df_list:
        data = pd.concat(df_list, ignore_index=True)

        # --- Basic Filters ---
        st.sidebar.header("Filters")
        influencers = st.sidebar.multiselect("Select Influencer(s)", options=data["Influencer"].unique())
        brands = st.sidebar.multiselect("Select Brand(s)", options=data["Brand"].unique())
        platforms = st.sidebar.multiselect("Select Platform(s)", options=data["Platform"].unique())

        # --- Apply Filters ---
        if influencers:
            data = data[data["Influencer"].isin(influencers)]
        if brands:
            data = data[data["Brand"].isin(brands)]
        if platforms:
            data = data[data["Platform"].isin(platforms)]

        # --- Show Key Metrics ---
        st.subheader("📌 Key Metrics")
        total_spend = data["Spend"].sum()
        total_roi = data["ROI"].sum()
        total_roas = (data["Revenue"] / data["Spend"]).mean() if "Revenue" in data.columns and "Spend" in data.columns else None

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"₹{total_spend:,.2f}")
        col2.metric("Total ROI", f"{total_roi:.2f}")
        col3.metric("Average ROAS", f"{total_roas:.2f}" if total_roas else "N/A")

        # --- Display Data ---
        st.subheader("📄 Filtered Campaign Data")
        st.dataframe(data, use_container_width=True)

    else:
        st.warning("No valid data found in uploaded files.")
else:
    st.info("Upload one or more Excel files to get started.")

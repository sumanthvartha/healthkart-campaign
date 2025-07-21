import streamlit as st
import pandas as pd
import plotly.express as px
import datetime
import io

from streamlit_option_menu import option_menu

st.set_page_config(page_title="Influencer Campaign Dashboard", layout="wide")

# --- Sidebar Navigation ---
with st.sidebar:
    selected = option_menu(
        menu_title="Main Menu",
        options=["Dashboard", "Upload Files", "Download Template"],
        icons=["bar-chart", "cloud-upload", "file-earmark-excel"],
        menu_icon="cast",
        default_index=0
    )

# --- Session State ---
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame()

# --- Template Download Page ---
if selected == "Download Template":
    st.title("📥 Download Excel Template")
    sample_df = pd.DataFrame({
        "Date": [datetime.date.today()],
        "Influencer": ["Amit"],
        "Brand": ["BrandX"],
        "Platform": ["Instagram"],
        "Reach": [50000],
        "Orders": [100],
        "Revenue": [20000],
        "Spend": [5000],
        "ROI": [4.0]
    })
    towrite = io.BytesIO()
    sample_df.to_excel(towrite, index=False, sheet_name="Template")
    towrite.seek(0)
    st.download_button("📥 Download Template File", towrite, file_name="template.xlsx")

# --- Upload Section ---
elif selected == "Upload Files":
    st.title("📤 Upload Influencer Campaign Data")
    uploaded_files = st.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

    if uploaded_files:
        df_list = []
        for file in uploaded_files:
            try:
                df = pd.read_excel(file)
                df["SourceFile"] = file.name
                df_list.append(df)
            except Exception as e:
                st.error(f"❌ Error reading {file.name}: {e}")

        if df_list:
            st.session_state.data = pd.concat(df_list, ignore_index=True)
            st.success("✅ Files uploaded and combined successfully.")
        else:
            st.warning("⚠️ No valid data found in uploaded files.")

# --- Dashboard Section ---
elif selected == "Dashboard":
    st.title("📊 Influencer Campaign Dashboard")

    if st.session_state.data.empty:
        st.info("📂 No data available. Please upload files first.")
    else:
        data = st.session_state.data

        # --- Filters ---
        with st.expander("🔍 Filter Options", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            influencers = col1.multiselect("Influencer", options=data["Influencer"].unique())
            brands = col2.multiselect("Brand", options=data["Brand"].unique())
            platforms = col3.multiselect("Platform", options=data["Platform"].unique())
            if "Date" in data.columns:
                data["Date"] = pd.to_datetime(data["Date"], errors='coerce')
                min_date, max_date = data["Date"].min().date(), data["Date"].max().date()
                start_date, end_date = col4.date_input("Date Range", [min_date, max_date])

        # --- Apply Filters ---
        if influencers:
            data = data[data["Influencer"].isin(influencers)]
        if brands:
            data = data[data["Brand"].isin(brands)]
        if platforms:
            data = data[data["Platform"].isin(platforms)]
        if "Date" in data.columns and start_date and end_date:
            data = data[(data["Date"].dt.date >= start_date) & (data["Date"].dt.date <= end_date)]

        # --- KPIs ---
        st.markdown("## 📌 Key Metrics")
        kpi1, kpi2, kpi3 = st.columns(3)
        total_spend = data["Spend"].sum()
        total_roi = data["ROI"].sum()
        avg_roas = (data["Revenue"] / data["Spend"]).mean()
        kpi1.metric("Total Spend", f"₹{total_spend:,.2f}")
        kpi2.metric("Total ROI", f"{total_roi:.2f}")
        kpi3.metric("Avg. ROAS", f"{avg_roas:.2f}")

        # --- Top Performers ---
        st.markdown("## 🏆 Top Performers")
        top_roi = data.sort_values(by="ROI", ascending=False).head(3)
        top_roas = data.copy()
        top_roas["ROAS"] = top_roas["Revenue"] / top_roas["Spend"]
        top_roas = top_roas.sort_values(by="ROAS", ascending=False).head(3)
        col1, col2 = st.columns(2)
        col1.dataframe(top_roi[["Influencer", "ROI"]])
        col2.dataframe(top_roas[["Influencer", "ROAS"]])

        # --- Charts ---
        st.markdown("## 📈 Visual Insights")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(data, x="Influencer", y="Spend", color="Brand", title="Spend by Influencer")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.bar(data, x="Influencer", y="Revenue", color="Platform", title="Revenue by Influencer")
            st.plotly_chart(fig2, use_container_width=True)

        # --- Data Table ---
        st.markdown("## 📄 Detailed Data")
        st.dataframe(data, use_container_width=True)

        # --- Download ---
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "filtered_data.csv")

        excel_io = io.BytesIO()
        with pd.ExcelWriter(excel_io, engine="xlsxwriter") as writer:
            data.to_excel(writer, index=False)
        st.download_button("Download Excel", excel_io.getvalue(), "filtered_data.xlsx")

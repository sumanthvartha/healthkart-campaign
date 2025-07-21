import streamlit as st
import pandas as pd
import io
import datetime
import plotly.express as px

st.set_page_config(page_title="Influencer Campaign Dashboard", layout="wide")
st.title("📊 Influencer Campaign Dashboard")

# --- Template File Download ---
with st.sidebar.expander("📥 Download Template"):
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
    st.download_button("Download Excel Template", towrite, file_name="template.xlsx")

# --- File Upload ---
st.sidebar.header("📤 Upload Excel Files")
uploaded_files = st.sidebar.file_uploader("Upload Excel files", type=["xlsx"], accept_multiple_files=True)

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
        data = pd.concat(df_list, ignore_index=True)

        # --- Check required columns ---
        required_columns = {"Influencer", "Brand", "Platform", "Spend", "Revenue", "ROI"}
        missing_cols = required_columns - set(data.columns)
        if missing_cols:
            st.error(f"❗ Missing required columns: {', '.join(missing_cols)}")
            st.stop()

        # --- Date Conversion ---
        if "Date" in data.columns:
            data["Date"] = pd.to_datetime(data["Date"], errors='coerce')

        # --- Sidebar Filters ---
        st.sidebar.header("🔍 Filters")

        # Search bar for influencer/brand
        search_influencer = st.sidebar.text_input("Search Influencer")
        search_brand = st.sidebar.text_input("Search Brand")

        influencers = st.sidebar.multiselect(
            "Select Influencer(s)",
            options=data["Influencer"].unique(),
            default=[] if search_influencer else data["Influencer"].unique()
        )
        if search_influencer:
            influencers = [inf for inf in data["Influencer"].unique() if search_influencer.lower() in inf.lower()]

        brands = st.sidebar.multiselect(
            "Select Brand(s)",
            options=data["Brand"].unique(),
            default=[] if search_brand else data["Brand"].unique()
        )
        if search_brand:
            brands = [b for b in data["Brand"].unique() if search_brand.lower() in b.lower()]

        platforms = st.sidebar.multiselect("Select Platform(s)", options=data["Platform"].unique())

        if "Date" in data.columns:
            min_date = data["Date"].min().date()
            max_date = data["Date"].max().date()
            start_date, end_date = st.sidebar.date_input("Select Date Range", [min_date, max_date])
        else:
            start_date, end_date = None, None

        # --- Apply Filters ---
        if influencers:
            data = data[data["Influencer"].isin(influencers)]
        if brands:
            data = data[data["Brand"].isin(brands)]
        if platforms:
            data = data[data["Platform"].isin(platforms)]
        if start_date and end_date and "Date" in data.columns:
            data = data[(data["Date"].dt.date >= start_date) & (data["Date"].dt.date <= end_date)]

        # --- Key Metrics ---
        st.subheader("📌 Key Metrics")
        total_spend = data["Spend"].sum()
        total_roi = data["ROI"].sum()
        avg_roas = (data["Revenue"] / data["Spend"]).mean() if "Revenue" in data.columns and "Spend" in data.columns else None

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"₹{total_spend:,.2f}")
        col2.metric("Total ROI", f"{total_roi:.2f}")
        col3.metric("Average ROAS", f"{avg_roas:.2f}" if avg_roas else "N/A")

        # --- Top Performers ---
        st.subheader("🏆 Top Performers")

        top_roi = data.sort_values(by="ROI", ascending=False).head(3)
        top_roas = data.copy()
        top_roas["ROAS"] = top_roas["Revenue"] / top_roas["Spend"]
        top_roas = top_roas.sort_values(by="ROAS", ascending=False).head(3)

        st.markdown("**Top 3 Influencers by ROI**")
        st.dataframe(top_roi[["Influencer", "Brand", "Platform", "ROI"]])

        st.markdown("**Top 3 Influencers by ROAS**")
        st.dataframe(top_roas[["Influencer", "Brand", "Platform", "ROAS"]])

        # --- Charts ---
        st.subheader("📈 Performance Charts")

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**Spend by Influencer**")
            spend_fig = px.bar(data, x="Influencer", y="Spend", color="Brand", title="Spend by Influencer")
            st.plotly_chart(spend_fig, use_container_width=True)

        with chart_col2:
            st.markdown("**Revenue by Influencer**")
            revenue_fig = px.bar(data, x="Influencer", y="Revenue", color="Platform", title="Revenue by Influencer")
            st.plotly_chart(revenue_fig, use_container_width=True)

        # --- Display Data ---
        st.subheader("📄 Filtered Campaign Data")
        st.dataframe(data, use_container_width=True)

        # --- Export Filtered Data ---
        st.subheader("📤 Export Filtered Data")
        csv = data.to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv, file_name="filtered_data.csv", mime="text/csv")

        excel_output = io.BytesIO()
        with pd.ExcelWriter(excel_output, engine="xlsxwriter") as writer:
            data.to_excel(writer, sheet_name="FilteredData", index=False)
        st.download_button("Download as Excel", excel_output.getvalue(), file_name="filtered_data.xlsx")
    else:
        st.warning("⚠️ No valid data found in uploaded files.")
else:
    st.info("📂 Upload one or more Excel files from the sidebar to get started.")

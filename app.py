import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="HealthKart Influencer Campaign Dashboard", layout="wide")

st.title("📊 HealthKart Influencer Campaign Dashboard")
st.write("Upload your campaign Excel file below to get started.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Show raw data
    with st.expander("View Raw Data"):
        st.dataframe(df)

    # --- Data Cleaning / Checks ---
    expected_cols = ["Influencer", "Platform", "Brand", "Product", "Influencer Type", "Post Count", 
                     "Reach", "Engagement", "Cost", "Revenue"]
    missing_cols = [col for col in expected_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing columns: {', '.join(missing_cols)}")
    else:
        # --- Filters ---
        st.sidebar.header("📂 Filter Campaign Data")
        brand_filter = st.sidebar.multiselect("Select Brand", options=df["Brand"].unique(), default=df["Brand"].unique())
        product_filter = st.sidebar.multiselect("Select Product", options=df["Product"].unique(), default=df["Product"].unique())
        influencer_filter = st.sidebar.multiselect("Influencer Type", options=df["Influencer Type"].unique(), default=df["Influencer Type"].unique())
        platform_filter = st.sidebar.multiselect("Platform", options=df["Platform"].unique(), default=df["Platform"].unique())

        filtered_df = df[
            df["Brand"].isin(brand_filter) &
            df["Product"].isin(product_filter) &
            df["Influencer Type"].isin(influencer_filter) &
            df["Platform"].isin(platform_filter)
        ]

        # --- KPI Metrics ---
        st.subheader("📈 Campaign Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Cost", f"₹{filtered_df['Cost'].sum():,.0f}")
        col2.metric("Total Revenue", f"₹{filtered_df['Revenue'].sum():,.0f}")
        col3.metric("ROI", f"{(filtered_df['Revenue'].sum() / filtered_df['Cost'].sum()):.2f}x")
        col4.metric("Incremental ROAS", f"{((filtered_df['Revenue'] - filtered_df['Cost']).sum() / filtered_df['Cost'].sum()):.2f}x")

        # --- Charts ---
        st.subheader("📊 Platform Performance")
        platform_perf = filtered_df.groupby("Platform")[["Reach", "Engagement", "Cost", "Revenue"]].sum().reset_index()
        fig1 = px.bar(platform_perf, x="Platform", y=["Reach", "Engagement"], barmode="group", title="Reach & Engagement by Platform")
        st.plotly_chart(fig1, use_container_width=True)

        fig2 = px.bar(platform_perf, x="Platform", y=["Cost", "Revenue"], barmode="group", title="Cost vs Revenue by Platform")
        st.plotly_chart(fig2, use_container_width=True)

        # --- Influencer Insights ---
        st.subheader("🌟 Influencer Performance")
        influencer_summary = filtered_df.groupby("Influencer").agg({
            "Reach": "sum",
            "Engagement": "sum",
            "Cost": "sum",
            "Revenue": "sum"
        }).reset_index()
        influencer_summary["ROI"] = influencer_summary["Revenue"] / influencer_summary["Cost"]
        top_influencers = influencer_summary.sort_values(by="ROI", ascending=False).head(5)
        poor_influencers = influencer_summary.sort_values(by="ROI", ascending=True).head(5)

        col5, col6 = st.columns(2)
        with col5:
            st.markdown("✅ Top Performing Influencers")
            st.dataframe(top_influencers)

        with col6:
            st.markdown("⚠️ Poor Performing Influencers")
            st.dataframe(poor_influencers)

        # --- Campaign Summary ---
        st.subheader("🎯 Top Campaigns by Product")
        top_campaigns = filtered_df.groupby("Product")[["Reach", "Engagement", "Revenue", "Cost"]].sum().reset_index()
        top_campaigns["ROI"] = top_campaigns["Revenue"] / top_campaigns["Cost"]
        st.dataframe(top_campaigns.sort_values(by="ROI", ascending=False))


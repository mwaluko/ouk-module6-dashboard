import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------
# 1. Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="OUK MSc Data Science | Interactive Sales & Sentiment Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---------------------------------------------------------
# 2. Header with OUK Logo & Student Metadata
# ---------------------------------------------------------
logo_path = Path(__file__).parent / "assets" / "ouk_logo.png"

header_col1, header_col2 = st.columns([1.2, 5.8], vertical_alignment="center")
with header_col1:
    if logo_path.exists():
        st.image(str(logo_path), width=140)
with header_col2:
    st.markdown(
        """
        <div style="background-color:#1C304A; padding:16px 22px; border-radius:10px; color:white;">
            <div style="font-size:12px; letter-spacing:1px; color:#78D2D2; font-weight:700;">
                OPEN UNIVERSITY OF KENYA (OUK) &nbsp;|&nbsp; MSC. DATA SCIENCE
            </div>
            <h2 style="margin:4px 0 6px 0; color:white; font-size:22px;">
                Module 6: Interactive Dashboard Development and Deployment — Mini-Project 1
            </h2>
            <div style="font-size:13px; color:#DCE6F1;">
                <strong>Student Name:</strong> MUTINDA Brian Mwaluko &nbsp;|&nbsp;
                <strong>Student ID:</strong> ST61/60459/2025 &nbsp;|&nbsp;
                <strong>Date:</strong> 25-Nov-2026
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# ---------------------------------------------------------
# 3. Cached Data Loader (Self-contained & Deployment-Safe)
# ---------------------------------------------------------
@st.cache_data
def load_sales_and_feedback_data() -> pd.DataFrame:
    """
    Generates a reproducible 360-record commercial & customer sentiment dataset
    combining online retail sales metrics with customer feedback sentiments,
    hourly timestamps, and geographic coordinates.
    """
    rng = np.random.default_rng(42)
    n = 360

    regions = ["North America", "Europe", "Asia", "Africa"]
    categories = [
        "Electronics",
        "Home Appliances",
        "Clothing",
        "Books",
        "Beauty Products",
        "Sports",
    ]
    sentiments = ["Positive", "Neutral", "Negative"]

    region_coords = {
        "North America": (39.8283, -98.5795),
        "Europe": (50.1109, 8.6821),
        "Asia": (34.0479, 100.6197),
        "Africa": (-1.2921, 36.8219),
    }

    sample_reviews = {
        "Positive": [
            "Fast delivery and outstanding product quality—exceeded expectations!",
            "Seamless checkout experience and great value for money.",
            "Customer support resolved my question within minutes. Highly recommend!",
            "Build quality is solid and arrived two days ahead of schedule.",
        ],
        "Neutral": [
            "Product matches the description, though packaging could be sturdier.",
            "Standard shipping speed; works as expected for the price point.",
            "Decent performance overall, still testing all features.",
            "Average experience—item arrived on time without issues.",
        ],
        "Negative": [
            "Delayed shipment and tracking updates stopped for three days.",
            "Item arrived with minor cosmetic damage; waiting on replacement.",
            "Instructions were unclear and setup took much longer than expected.",
            "Price feels high compared to similar alternatives in this category.",
        ],
    }

    chosen_regions = rng.choice(regions, size=n, p=[0.32, 0.26, 0.25, 0.17])
    chosen_categories = rng.choice(categories, size=n)
    chosen_sentiments = rng.choice(sentiments, size=n, p=[0.54, 0.27, 0.19])

    base_prices = {
        "Electronics": 420.0,
        "Home Appliances": 310.0,
        "Clothing": 85.0,
        "Books": 35.0,
        "Beauty Products": 65.0,
        "Sports": 145.0,
    }

    units = rng.integers(1, 8, size=n)
    revenues = [
        round(base_prices[cat] * u * rng.uniform(0.85, 1.25), 2)
        for cat, u in zip(chosen_categories, units)
    ]

    hours = rng.integers(0, 24, size=n)
    dates = pd.date_range("2026-01-01", "2026-11-20", periods=n)

    lats, lons, texts = [], [], []
    for reg, sent in zip(chosen_regions, chosen_sentiments):
        base_lat, base_lon = region_coords[reg]
        lats.append(base_lat + rng.normal(0, 3.5))
        lons.append(base_lon + rng.normal(0, 4.5))
        texts.append(rng.choice(sample_reviews[sent]))

    return pd.DataFrame(
        {
            "Order_ID": [f"ORD-{1000 + i}" for i in range(n)],
            "Date": pd.to_datetime(dates).date,
            "Hour": hours,
            "Region": chosen_regions,
            "Product_Category": chosen_categories,
            "Units_Sold": units,
            "Total_Revenue": revenues,
            "Sentiment": chosen_sentiments,
            "Customer_Feedback": texts,
            "lat": lats,
            "lon": lons,
        }
    )


df = load_sales_and_feedback_data()

# ---------------------------------------------------------
# 4. Sidebar Interactive Controls
# ---------------------------------------------------------
if logo_path.exists():
    st.sidebar.image(str(logo_path), width=110)

st.sidebar.header("Dashboard Filter Controls")
st.sidebar.markdown("Customize slices across sales performance and customer sentiment:")

selected_regions = st.sidebar.multiselect(
    "Select Region(s):",
    options=sorted(df["Region"].unique()),
    default=sorted(df["Region"].unique()),
)

selected_categories = st.sidebar.multiselect(
    "Select Product Category(s):",
    options=sorted(df["Product_Category"].unique()),
    default=sorted(df["Product_Category"].unique()),
)

selected_sentiments = st.sidebar.multiselect(
    "Select Customer Sentiment(s):",
    options=["Positive", "Neutral", "Negative"],
    default=["Positive", "Neutral", "Negative"],
)

st.sidebar.subheader("Hourly Activity Filter")
selected_hour = st.sidebar.slider("Select Hour of Day (0–23):", 0, 23, 14)

st.sidebar.subheader("Display Options")
chart_style = st.sidebar.selectbox(
    "Sentiment Chart Type:",
    options=["Bar Chart", "Pie Chart"],
)
show_raw_data = st.sidebar.checkbox("Show Filtered Dataset Table", value=False)

# Apply filters
filtered_df = df[
    (df["Region"].isin(selected_regions))
    & (df["Product_Category"].isin(selected_categories))
    & (df["Sentiment"].isin(selected_sentiments))
]

if filtered_df.empty:
    st.warning("No records match your current filter selection. Please select at least one option in each filter.")
    st.stop()

# ---------------------------------------------------------
# 5. Top-Level KPI Summary Metrics
# ---------------------------------------------------------
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Revenue", f"${filtered_df['Total_Revenue'].sum():,.2f}")
kpi2.metric("Average Order Revenue", f"${filtered_df['Total_Revenue'].mean():,.2f}")
kpi3.metric("Total Orders", f"{len(filtered_df):,}")
positive_share = (filtered_df["Sentiment"] == "Positive").mean() * 100
kpi4.metric("Positive Sentiment Rate", f"{positive_share:.1f}%")

st.markdown("---")

# ---------------------------------------------------------
# 6. Tabbed Interactive Visualizations (Plotly)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "📊 Sales by Product & Region",
        "💬 Customer Sentiment Breakdown",
        "🕒 Hourly & Geographic Activity",
        "🔍 Random Feedback Explorer",
    ]
)

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Revenue by Product Category")
        prod_summary = (
            filtered_df.groupby("Product_Category", as_index=False)["Total_Revenue"]
            .sum()
            .sort_values("Total_Revenue", ascending=False)
        )
        fig_prod = px.bar(
            prod_summary,
            x="Product_Category",
            y="Total_Revenue",
            color="Product_Category",
            text_auto=".2s",
            title="Total Revenue by Product Category ($)",
            labels={"Product_Category": "Product Category", "Total_Revenue": "Total Revenue ($)"},
        )
        fig_prod.update_layout(showlegend=False)
        st.plotly_chart(fig_prod, use_container_width=True)

    with c2:
        st.subheader("Revenue Share by Region")
        reg_summary = (
            filtered_df.groupby("Region", as_index=False)["Total_Revenue"]
            .sum()
        )
        fig_reg = px.pie(
            reg_summary,
            names="Region",
            values="Total_Revenue",
            hole=0.35,
            title="Regional Revenue Distribution",
        )
        st.plotly_chart(fig_reg, use_container_width=True)

with tab2:
    s1, s2 = st.columns(2)
    with s1:
        st.subheader(f"Overall Sentiment Distribution ({chart_style})")
        sent_counts = (
            filtered_df["Sentiment"]
            .value_counts()
            .reset_index()
        )
        sent_counts.columns = ["Sentiment", "Count"]
        color_map = {"Positive": "#2E8B57", "Neutral": "#4682B4", "Negative": "#D9534F"}

        if chart_style == "Bar Chart":
            fig_sent = px.bar(
                sent_counts,
                x="Sentiment",
                y="Count",
                color="Sentiment",
                color_discrete_map=color_map,
                text_auto=True,
                title="Customer Feedback Count by Sentiment",
            )
        else:
            fig_sent = px.pie(
                sent_counts,
                names="Sentiment",
                values="Count",
                color="Sentiment",
                color_discrete_map=color_map,
                title="Customer Feedback Share by Sentiment",
            )
        st.plotly_chart(fig_sent, use_container_width=True)

    with s2:
        st.subheader("Sentiment Breakdown Across Product Categories")
        cat_sent = (
            filtered_df.groupby(["Product_Category", "Sentiment"], as_index=False)
            .size()
            .rename(columns={"size": "Feedback_Count"})
        )
        fig_grouped = px.bar(
            cat_sent,
            x="Product_Category",
            y="Feedback_Count",
            color="Sentiment",
            barmode="group",
            color_discrete_map=color_map,
            title="Sentiment Counts by Product Category",
            labels={"Product_Category": "Product Category", "Feedback_Count": "Count"},
        )
        st.plotly_chart(fig_grouped, use_container_width=True)

with tab3:
    st.subheader(f"Orders & Feedback Logged During Hour {selected_hour}:00 – {selected_hour}:59")
    hourly_df = filtered_df[filtered_df["Hour"] == selected_hour]
    st.info(f"**{len(hourly_df)}** matching order(s) recorded between **{selected_hour}:00** and **{selected_hour}:59**.")
    if not hourly_df.empty:
        st.map(hourly_df[["lat", "lon"]])
    else:
        st.write("No records for the chosen hour under current region/category filters. Adjust the hour slider in the sidebar.")

with tab4:
    st.subheader("Inspect Random Customer Feedback by Sentiment")
    radio_sent = st.radio(
        "Choose Sentiment Category:",
        options=["Positive", "Neutral", "Negative"],
        horizontal=True,
    )
    matching_reviews = df[df["Sentiment"] == radio_sent]
    if st.button("Draw Another Random Review") or True:
        sample_row = matching_reviews.sample(n=1).iloc[0]
        st.success(
            f"**[{sample_row['Sentiment']} | {sample_row['Product_Category']} | {sample_row['Region']}]** "
            f"— *"{sample_row['Customer_Feedback']}"* (Order `{sample_row['Order_ID']}`, Revenue: `${sample_row['Total_Revenue']:,.2f}`)"
        )

# ---------------------------------------------------------
# 7. Optional Raw Data Table View
# ---------------------------------------------------------
if show_raw_data:
    st.markdown("---")
    st.subheader("Filtered Dataset Preview")
    st.dataframe(
        filtered_df.drop(columns=["lat", "lon"]),
        use_container_width=True,
    )

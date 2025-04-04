import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.metric_cards import style_metric_cards

# Page setup
st.set_page_config(page_title="📊 Analytics Dashboard", page_icon="📈", layout="wide")

# Tooltip / info
st.markdown(
    '<p style="color: gray; font-size: 12px;">⚠️ You can filter the data below. All visualizations reflect the filtered results. Do not rename columns.</p>',
    unsafe_allow_html=True
)

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

df = load_data()
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')

# 👉 Main filter section
st.subheader("🔍 Filter & Explore Dataset", divider="rainbow")
filtered_df = dataframe_explorer(df, case=False)
st.dataframe(filtered_df, use_container_width=True)

# Handle empty filtered data
if filtered_df.empty:
    st.warning("⚠️ No data available after filtering. Please adjust filters.")
    st.stop()

# 👉 Business Metrics
st.subheader("📈 Business Metrics", divider="rainbow")

col1, col2 = st.columns(2)

with col1:
    source = pd.DataFrame({
        "Quantity": filtered_df["Quantity"],
        "Product": filtered_df["Product"]
    })
    bar_chart = alt.Chart(source).mark_bar().encode(
        x="sum(Quantity):Q",
        y=alt.Y("Product:N", sort="-x")
    )
    st.altair_chart(bar_chart, use_container_width=True)

with col2:
    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric("Total Products", filtered_df["Product"].count())
    metric_col2.metric("Total Price (USD)", f"{filtered_df['TotalPrice'].sum():,.0f}")

    metric_col3, metric_col4, metric_col5 = st.columns(3)
    metric_col3.metric("Max Price", f"{filtered_df['TotalPrice'].max():,.0f}")
    metric_col4.metric("Min Price", f"{filtered_df['TotalPrice'].min():,.0f}")
    metric_col5.metric("Price Range", f"{filtered_df['TotalPrice'].max() - filtered_df['TotalPrice'].min():,.0f}")

    style_metric_cards(border_left_color="#415a7d", border_color="#1f66bd")

# 👉 Dot Plot
col3, col4 = st.columns(2)
with col3:
    st.subheader("🔵 Products vs. Total Price", divider="rainbow")
    dot_chart = alt.Chart(filtered_df).mark_circle().encode(
        x='Product',
        y='TotalPrice',
        color='Category'
    ).interactive()
    st.altair_chart(dot_chart, use_container_width=True)

# 👉 Unit Price by Month
with col4:
    st.subheader("📅 Monthly Unit Price", divider="rainbow")
    month_chart = alt.Chart(filtered_df).mark_bar().encode(
        x="month(OrderDate):O",
        y="sum(UnitPrice):Q",
        color="Product:N"
    )
    st.altair_chart(month_chart, use_container_width=True)

# 👉 Scatter Plot
col5, col6 = st.columns(2)
with col5:
    st.subheader("📌 Scatter Plot", divider="rainbow")
    feature_x = st.selectbox('X-axis Feature', filtered_df.select_dtypes("object").columns, key="scatter_x")
    feature_y = st.selectbox('Y-axis Feature', filtered_df.select_dtypes("number").columns, key="scatter_y")
    scatter_fig = px.scatter(
        filtered_df, x=feature_x, y=feature_y, color='Product',
        title=f'{feature_x} vs {feature_y}', template="plotly_white"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

# 👉 Histogram
with col6:
    st.subheader("📊 Histogram", divider="rainbow")
    hist_feature = st.selectbox("Select Feature", filtered_df.select_dtypes("object").columns, key="hist_feature")
    hist_fig = px.histogram(filtered_df, x=hist_feature, nbins=20, template="plotly_white")
    st.plotly_chart(hist_fig, use_container_width=True)


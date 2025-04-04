import streamlit as st 
import pandas as pd
import altair as alt 
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer

# Configure the page width 
st.set_page_config(page_title="Analytics", page_icon="🌎", layout="wide")

# Streamlit theme = None
theme_plotly = None 

# Refresh Button
if st.button("🔄 Refresh Dashboard"):
    st.experimental_set_query_params()

# Tooltip Message
tooltip_message = (
    "⚠️ The dataset is a working process. You cannot open the Excel file directly, "
    "and no modifications can be made. You can only add data to existing columns, "
    "and column names cannot be changed."
)
st.markdown(
    f'<p style="color: gray; font-size: 12px;">{tooltip_message}</p>',
    unsafe_allow_html=True
)

# Function to load dataset
@st.cache_data
def load_data():
    return pd.read_csv('data.csv')

df = load_data()

# Ensure 'OrderDate' is in datetime format
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Display dataset preview
with st.expander("📊 View Dataset"):
    st.dataframe(df, use_container_width=True)

# Business Metrics Heading
st.subheader("📈 Business Metrics")

# Check if df is empty
if df.empty:
    st.warning("⚠️ No data available. Please check your dataset.")
    st.stop()

# Create two columns for layout
col1, col2 = st.columns(2)

# Bar Chart - Products & Quantities
with col1:
    st.subheader("Products & Quantities", divider="rainbow")
    source = pd.DataFrame({
        "Quantity ($)": df["Quantity"],
        "Product": df["Product"]
    })
    bar_chart = alt.Chart(source).mark_bar().encode(
        x="sum(Quantity ($)):Q",
        y=alt.Y("Product:N", sort="-x")
    )
    st.altair_chart(bar_chart, use_container_width=True, theme=theme_plotly)

# Data Metrics
with col2:
    st.subheader("Data Metrics", divider="rainbow")
    from streamlit_extras.metric_cards import style_metric_cards

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Total Inventory Products", value=df["Product"].count())
    metric_col2.metric(label="Total Price (USD)", value=f"{df['TotalPrice'].sum():,.0f}")

    metric_col3, metric_col4, metric_col5 = st.columns(3)
    metric_col3.metric(label="Max Price (USD)", value=f"{df['TotalPrice'].max():,.0f}")
    metric_col4.metric(label="Min Price (USD)", value=f"{df['TotalPrice'].min():,.0f}")
    metric_col5.metric(label="Price Range (USD)", value=f"{df['TotalPrice'].max() - df['TotalPrice'].min():,.0f}")

    # Style metrics
    style_metric_cards(border_left_color="#415a7d", border_color="#1f66bd")

# Dot Plot - Products & Total Price
col3, col4 = st.columns(2)
with col3:
    st.subheader("Products & Total Price", divider="rainbow")
    dot_chart = alt.Chart(df).mark_circle().encode(
        x='Product',
        y='TotalPrice',
        color='Category',
    ).interactive()
    st.altair_chart(dot_chart, use_container_width=True)

# Bar Graph - Products & Unit Price (By Month)
with col4:
    st.subheader("Products & Unit Price", divider="rainbow")
    unit_price_chart = alt.Chart(df).mark_bar().encode(
        x="month(OrderDate):O",
        y="sum(UnitPrice):Q",
        color="Product:N"
    )
    st.altair_chart(unit_price_chart, use_container_width=True, theme=theme_plotly)

# Scatter Plot
col5, col6 = st.columns(2)
with col5:
    st.subheader("Features by Frequency (Scatter Plot)", divider="rainbow")
    feature_x = st.selectbox('X-axis Feature', df.select_dtypes("object").columns, key="scatter_x")
    feature_y = st.selectbox('Y-axis Feature', df.select_dtypes("number").columns, key="scatter_y")

    scatter_fig = px.scatter(
        df, x=feature_x, y=feature_y, color='Product',
        title=f'Scatter Plot: {feature_x} vs {feature_y}', template="plotly_white"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

# Histogram
with col6:
    st.subheader("Histogram of Selected Feature", divider="rainbow")
    hist_feature = st.selectbox('Select a feature', df.select_dtypes("object").columns, key="hist_feature")

    hist_fig = px.histogram(df, x=hist_feature, nbins=20, template="plotly_white")
    st.plotly_chart(hist_fig, use_container_width=True)

        nbins=20,
        title=f'Histogram of {feature}',
        labels={feature: feature},
        template="plotly_white"
    )
    st.plotly_chart(fig_hist, use_container_width=True)

import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
from streamlit_extras.dataframe_explorer import dataframe_explorer

# Configure Streamlit Page
st.set_page_config(page_title="Analytics", page_icon="🌎", layout="wide")

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

# Function to load default data
@st.cache_data
def load_default_data():
    return pd.read_csv('data.csv')

# Function to load uploaded files (CSV)
def load_uploaded_file(uploaded_file):
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        else:
            st.sidebar.error("Unsupported file type! Please upload a CSV file.")
            st.stop()
    except Exception as e:
        st.sidebar.error(f"Error loading file: {e}")
        st.stop()

# Sidebar for file upload or default dataset
st.sidebar.title("📂 Upload or Load Dataset")

data_source = st.sidebar.radio("Choose Data Source:", ("Default Dataset", "Upload Your Own Dataset"))

if data_source == "Default Dataset":
    df = load_default_data()
    st.sidebar.success("✅ Default dataset loaded successfully!")
else:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=['csv'])
    if uploaded_file is not None:
        df = load_uploaded_file(uploaded_file)
        st.sidebar.success("✅ Dataset uploaded successfully!")
    else:
        st.sidebar.warning("⚠️ Please upload a dataset to proceed.")
        st.stop()

# Ensure 'OrderDate' column is in datetime format
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce')

# Sidebar for Date Filter
st.sidebar.title("📅 Select Date Range")
start_date = st.sidebar.date_input("Start Date", value=df['OrderDate'].min(), min_value=df['OrderDate'].min(), max_value=df['OrderDate'].max())
end_date = st.sidebar.date_input("End Date", value=df['OrderDate'].max(), min_value=df['OrderDate'].min(), max_value=df['OrderDate'].max())

# Filter dataset based on date range
df_filtered = df[(df['OrderDate'] >= pd.to_datetime(start_date)) & (df['OrderDate'] <= pd.to_datetime(end_date))]

# Check if filtered data is empty
if df_filtered.empty:
    st.warning("⚠️ No data available for the selected date range.")
    st.stop()

# Show Filtered Data in Expandable Section
with st.expander("📊 View Filtered Dataset"):
    filtered_df = dataframe_explorer(df_filtered, case=False)
    st.dataframe(filtered_df, use_container_width=True)

# Business Metrics Heading
st.subheader(f"📈 Business Metrics ({start_date} - {end_date})")

# Create two columns for layout
col1, col2 = st.columns(2)

# Bar Chart - Products & Quantities
with col1:
    st.subheader("📦 Products & Quantities", divider="rainbow")
    source = pd.DataFrame({
        "Quantity": df_filtered["Quantity"],
        "Product": df_filtered["Product"]
    })
    bar_chart = alt.Chart(source).mark_bar().encode(
        x="sum(Quantity):Q",
        y=alt.Y("Product:N", sort="-x")
    )
    st.altair_chart(bar_chart, use_container_width=True)

# Data Metrics
with col2:
    st.subheader("📊 Data Metrics", divider="rainbow")
    from streamlit_extras.metric_cards import style_metric_cards

    metric_col1, metric_col2 = st.columns(2)
    metric_col1.metric(label="Total Inventory Products", value=df_filtered["Product"].count())
    metric_col2.metric(label="Total Price (USD)", value=f"{df_filtered['TotalPrice'].sum():,.0f}")

    metric_col3, metric_col4, metric_col5 = st.columns(3)
    metric_col3.metric(label="Max Price (USD)", value=f"{df_filtered['TotalPrice'].max():,.0f}")
    metric_col4.metric(label="Min Price (USD)", value=f"{df_filtered['TotalPrice'].min():,.0f}")
    metric_col5.metric(label="Price Range (USD)", value=f"{df_filtered['TotalPrice'].max() - df_filtered['TotalPrice'].min():,.0f}")

    # Style metrics
    style_metric_cards(border_left_color="#415a7d", border_color="#1f66bd")

# Dot Plot - Products & Total Price
col3, col4 = st.columns(2)
with col3:
    st.subheader("💰 Products & Total Price", divider="rainbow")
    dot_chart = alt.Chart(df_filtered).mark_circle().encode(
        x='Product',
        y='TotalPrice',
        color='Category'
    ).interactive()
    st.altair_chart(dot_chart, use_container_width=True)

# Bar Graph - Products & Unit Price (By Month)
with col4:
    st.subheader("📊 Products & Unit Price", divider="rainbow")
    unit_price_chart = alt.Chart(df_filtered).mark_bar().encode(
        x="month(OrderDate):O",
        y="sum(UnitPrice):Q",
        color="Product:N"
    )
    st.altair_chart(unit_price_chart, use_container_width=True)

# Scatter Plot
col5, col6 = st.columns(2)
with col5:
    st.subheader("📉 Features by Frequency (Scatter Plot)", divider="rainbow")
    feature_x = st.selectbox('X-axis Feature', df_filtered.select_dtypes("object").columns, key="scatter_x")
    feature_y = st.selectbox('Y-axis Feature', df_filtered.select_dtypes("number").columns, key="scatter_y")

    scatter_fig = px.scatter(
        df_filtered, x=feature_x, y=feature_y, color='Product',
        title=f'Scatter Plot: {feature_x} vs {feature_y}', template="plotly_white"
    )
    st.plotly_chart(scatter_fig, use_container_width=True)

# Histogram
with col6:
    st.subheader("📊 Histogram of Selected Feature", divider="rainbow")
    hist_feature = st.selectbox('Select a feature', df_filtered.select_dtypes("object").columns, key="hist_feature")

    hist_fig = px.histogram(df_filtered, x=hist_feature, nbins=20, template="plotly_white")
    st.plotly_chart(hist_fig, use_container_width=True)

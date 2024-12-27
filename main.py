import streamlit as st 
import pandas as pd
import plotly.express as px
import seaborn as sns 
import altair as alt 
from matplotlib import pyplot as plt 
from streamlit_extras.dataframe_explorer import dataframe_explorer
# confid the page width 
st.set_page_config(page_title="Analytics", page_icon="🌎", layout="wide")

#streamlit theme=none
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
# load data set 

# Function to load default data (data.csv)
@st.cache_data
def load_default_data():
    return pd.read_csv(r'c:\Users\Extreme\OneDrive\Desktop\streamlit  dashboards\bussiness_dashboard\data.csv')

# Function to load uploaded files (supports CSV)
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
st.sidebar.title("Upload or Load Dataset")

data_source = st.sidebar.radio(
    "Choose Data Source:",
    ("Default Dataset", "Upload Your Own Dataset")
)

# Load dataset based on user input
if data_source == "Default Dataset":
    df = load_default_data()
    st.sidebar.success("Default dataset loaded successfully!")
else:
    uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=['csv'])

    if uploaded_file is not None:
        df = load_uploaded_file(uploaded_file)
        st.sidebar.success("Dataset uploaded successfully!")
    else:
        st.sidebar.warning("Please upload a dataset to proceed.")
        st.stop()

# side bar 
# st.sidebar.image("")
# side bar date picker 
# Ensure 'OrderDate' is in datetime format
df['OrderDate'] = pd.to_datetime(df['OrderDate'])

# Sidebar for date selection
with st.sidebar:
    st.title("Select Date Range")
    start_date = st.date_input("Start Date", value=df['OrderDate'].min(), min_value=df['OrderDate'].min(), max_value=df['OrderDate'].max())
    end_date = st.date_input("End Date", value=df['OrderDate'].max(), min_value=df['OrderDate'].min(), max_value=df['OrderDate'].max())

# Provide a message for the selected date range
st.error(f"Business Metrics between [{start_date}] and [{end_date}]")

# Compare and filter date range
df2 = df[(df['OrderDate'] >= pd.to_datetime(start_date)) & (df['OrderDate'] <= pd.to_datetime(end_date))]

# Expandable section for filtered data
with st.expander("Filter Data:"):
    filtered_df = dataframe_explorer(df2, case=False)
    st.dataframe(filtered_df, use_container_width=True)

b1, b2=st.columns(2)

#bar chart
with b1:  
 st.subheader('Products & Qantities', divider='rainbow',)
 source = pd.DataFrame({
        "Quantity ($)": df2["Quantity"],
        "Product": df2["Product"]
      })
 
 bar_chart = alt.Chart(source).mark_bar().encode(
        x="sum(Quantity ($)):Q",
        y=alt.Y("Product:N", sort="-x")
    )
 st.altair_chart(bar_chart, use_container_width=True,theme=theme_plotly)
 
# metrics 
with b2:
    st.subheader("Data Metrics",divider="rainbow")
    from streamlit_extras.metric_cards import style_metric_cards
    col1, col2, = st.columns(2)
    col1.metric(label="All Inventory Products ", value=df2.Product.count(), delta="Number of Items in stock")
    col2.metric(label="Sum of Product Price USD:", value= f"{df2.TotalPrice.sum():,.0f}",delta=df2.TotalPrice.median())

    col11, col22,col33, = st.columns(3)
    col11.metric(label="Maximum Price  USD:", value= f"{ df2.TotalPrice.max():,.0f}",delta="High Price")
    col22.metric(label="Minimum Price  USD:", value= f"{ df2.TotalPrice.min():,.0f}",delta="Low Price")
    col33.metric(label="Total Price Range  USD:", value= f"{ df2.TotalPrice.max()-df2.TotalPrice.min():,.0f}",delta="Annual Salary Range")
    # style the matrics
    style_metric_cards(background_color="defult",border_left_color="#415a7d",border_color="#1f66bd",box_shadow="938f8c")


#dot Plot
a1,a2=st.columns(2)
with a1:
    st.subheader('Products & Total Price', divider='rainbow',)
    source = df2
    chart = alt.Chart(source).mark_circle().encode(
        x='Product',
        y='TotalPrice',
        color='Category',
    ).interactive()
    st.altair_chart(chart, theme="streamlit", use_container_width=True)


with a2:
    st.subheader('Products & Unit Price', divider='rainbow',)
    energy_source = pd.DataFrame({
        "Product": df2["Product"],
        "UnitPrice ($)":  df2["UnitPrice"],
        "Date": df2["OrderDate"]
        })
    
    #bar Graph
    bar_chart = alt.Chart(energy_source).mark_bar().encode(
            x="month(Date):O",
            y="sum(UnitPrice ($)):Q",
            color="Product:N"
        )
    st.altair_chart(bar_chart, use_container_width=True,theme=theme_plotly)
    
p1,p2=st.columns(2) 
with p1:
    # Select features to display scatter plot
    st.subheader('Features by Frequency', divider='rainbow',)
    feature_x = st.selectbox('Select feature for x Qualitative data', df2.select_dtypes("object").columns)
    feature_y = st.selectbox('Select feature for y Quantitative Data', df2.select_dtypes("number").columns)

    # Display scatter plot
    fig, ax = plt.subplots()
    sns.scatterplot(data=df2, x=feature_x, y=feature_y, hue=df.Product, ax=ax)
    st.pyplot(fig)


with p2:
    st.subheader('Features by Frequency', divider='rainbow',)
    feature = st.selectbox('Select a feature', df2.select_dtypes("object").columns)
    # Plot histogram
    fig, ax = plt.subplots()
    ax.hist(df2[feature], bins=20)

    # Set the title and labels
    ax.set_title(f'Histogram of {feature}')
    ax.set_xlabel(feature)
    ax.set_ylabel('Frequency')

    # Display the plot
    st.pyplot(fig)
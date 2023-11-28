import time
import pandas as pd
import plotly.express as px
import streamlit as st
from test_data import generate_plane_movements

st.set_page_config(
    page_title="Real-Time Plane Movements Dashboard",
    page_icon="✈️",
    layout="wide",
)

# Function to generate data
def get_data() -> pd.DataFrame:
    return generate_plane_movements()

# Initialize session state for the filter if it doesn't exist
if 'plane_type_filter' not in st.session_state:
    st.session_state['plane_type_filter'] = 'All'

# Dashboard title
st.title("Real-Time / Live Plane Movements Dashboard")

# Get the data
df = get_data()

# Add an option to select all plane types
all_types = ["All"] + sorted(list(pd.unique(df["plane_type"])))

# Use the session state to store the selected filter option
selected_type = st.selectbox("Select the Plane Type", all_types, index=all_types.index(st.session_state['plane_type_filter']))

# Update the session state only when the user changes the selection
if selected_type != st.session_state['plane_type_filter']:
    st.session_state['plane_type_filter'] = selected_type

# Creating a single-element container
placeholder = st.empty()

# Near real-time / live feed simulation
for seconds in range(200):
    # Simulate data updates (if applicable)
    df = get_data()

    # Apply the filter only if a specific plane type is selected
    if st.session_state['plane_type_filter'] != "All":
        df = df[df["plane_type"] == st.session_state['plane_type_filter']]

    with placeholder.container():
        # Create three columns for charts
        fig_col1, fig_col2, fig_col3 = st.columns(3)
        with fig_col1:
            st.markdown("### Flight Map")
            fig = px.scatter_geo(df, lat='lat', lon='lon', hover_name='title')
            fig.update_layout({"uirevision": "foo"}, overwrite=True)
            st.write(fig)
            
        with fig_col2:
            st.markdown("### Plane Type Distribution")
            fig2 = px.histogram(data_frame=df, x="plane_type")
            st.write(fig2)

        with fig_col3:
            st.markdown("### Streamlit Map")
            st.map(df[['lat', 'lon']])

        st.markdown("### Detailed Data View")
        st.dataframe(df)

        time.sleep(1)

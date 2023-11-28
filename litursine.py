import streamlit as st
import time
from test_data import generate_plane_movements

# Use Streamlit's caching to only update data when needed
@st.cache(allow_output_mutation=True)
def get_data():
    return generate_plane_movements()

def main():
    st.title("Live Plane Movements Dashboard")

    # Create placeholders for the map and table
    map_placeholder = st.empty()
    table_placeholder = st.empty()

    while True:
        # Get updated data
        data = get_data()

        # Update map and table in their respective placeholders
        with map_placeholder.container():
            st.map(data[['lat', 'lon']])

        with table_placeholder.container():
            st.dataframe(data)

        # Sleep for 5 seconds before the next update
        time.sleep(5)

if __name__ == "__main__":
    main()

# Import necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import time

# Initialize the Dash app
app = dash.Dash(__name__)

UPDATE_INTERVAL = 10

# Global variable to store previous data
global previous_df
previous_df = pd.DataFrame()

# Variable to store the next update timestamp
global next_update_time
next_update_time = time.time() + UPDATE_INTERVAL

# Layout of the Dash app
app.layout = html.Div([
    dcc.Interval(
        id='data-interval-component',
        interval=UPDATE_INTERVAL * 1000,
        n_intervals=0
    ),
    dcc.Interval(
        id='countdown-interval-component',
        interval=1 * 1000,
        n_intervals=0
    ),
    html.H1("CSV Data Dashboard"),
    html.Div(id='csv-data'),
    html.P(id='update-time'),
])

# Function to read CSV data
def read_csv_data():
    return pd.read_csv('schedule.csv')

# Function to compare dataframes and highlight changes
def highlight_changes(current_df, previous_df):
    # Generate HTML from the current dataframe
    current_html = current_df.to_html()

    # Find new and removed items
    new_items = current_df[~current_df.isin(previous_df)].dropna()
    removed_items = previous_df[~previous_df.isin(current_df)].dropna()

    # Apply HTML styling for new and removed items
    for row_index in new_items.index:
        current_html = current_html.replace(f'<tr>', f'<tr style="background-color: green;">', 1)

    for row_index in removed_items.index:
        current_html = current_html.replace(f'<tr>', f'<tr style="background-color: red;">', 1)

    return current_html

    
# Callback to update the data
@app.callback(Output('csv-data', 'children'), Input('data-interval-component', 'n_intervals'))
def update_data(n):
    global next_update_time, previous_df
    current_df = read_csv_data()
    
    # Compare and highlight changes
    csv_data = highlight_changes(current_df, previous_df)
    
    # Update previous dataframe
    previous_df = current_df.copy()

    # Render the HTML using Markdown
    markdown_content = dcc.Markdown(csv_data, dangerously_allow_html=True)

    # Calculate remaining time until the next update
    current_time = time.time()
    remaining_seconds = int(next_update_time - current_time)
    
    # If it's time for the next update, update next_update_time
    if remaining_seconds <= 0:
        next_update_time = current_time + UPDATE_INTERVAL
    
    return markdown_content


# Callback to update the countdown timer
@app.callback(Output('update-time', 'children'), Input('countdown-interval-component', 'n_intervals'))
def update_countdown(n):
    global next_update_time
    current_time = time.time()
    remaining_seconds = int(next_update_time - current_time)

    if remaining_seconds <= 0:
        next_update_time = current_time + UPDATE_INTERVAL

    time_until_next_update = f"Next refresh in: {remaining_seconds} seconds"

    return time_until_next_update

if __name__ == '__main__':
    app.run_server(debug=True)

# Import necessary libraries
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import time

# Initialize the Dash app
app = dash.Dash(__name__)

UPDATE_INTERVAL = 10

# Variable to store the next update timestamp
global next_update_time 
next_update_time = time.time() + UPDATE_INTERVAL  # Initial next update time

# Layout of the Dash app
app.layout = html.Div([
    dcc.Interval(
        id='data-interval-component',
        interval=UPDATE_INTERVAL * 1000,  # in milliseconds, UPDATE_INTERVAL seconds
        n_intervals=0
    ),
    dcc.Interval(
        id='countdown-interval-component',
        interval=1 * 1000,  # in milliseconds, 1 second
        n_intervals=0
    ),
    html.H1("CSV Data Dashboard"),
    dcc.Markdown(id='csv-data', dangerously_allow_html=True),
    html.P(id='update-time'),
])

# Function to read CSV data
def read_csv_data():
    df = pd.read_csv('schedule.csv')
    return df.to_html(escape=False)  # Use escape=False to allow HTML rendering

# Callback to update the data
@app.callback(Output('csv-data', 'children'), Input('data-interval-component', 'n_intervals'))
def update_data(n):
    global next_update_time
    csv_data = read_csv_data()
    
    # Calculate remaining time until the next update
    current_time = time.time()
    remaining_seconds = int(next_update_time - current_time)
    
    # If it's time for the next update, update next_update_time
    if remaining_seconds <= 0:
        
        next_update_time = current_time + UPDATE_INTERVAL
    
    return csv_data

# Callback to update the countdown timer
@app.callback(Output('update-time', 'children'), Input('countdown-interval-component', 'n_intervals'))
def update_countdown(n):
    global next_update_time  # Access the global variable
    current_time = time.time()
    remaining_seconds = int(next_update_time - current_time)
    
    # If it's time for the next update, update next_update_time
    if remaining_seconds <= 0:
        next_update_time = current_time + UPDATE_INTERVAL
    
    time_until_next_update = f"Next refresh in: {remaining_seconds} seconds"
    
    return time_until_next_update

if __name__ == '__main__':
    app.run_server(debug=True)

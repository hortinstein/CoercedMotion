import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_table import DataTable
import pandas as pd
import plotly.express as px
import datetime

from test_data import generate_plane_movements

# Global variables to store the previous state and flight data
previous_df = pd.DataFrame()
previous_df = generate_plane_movements(None)
flight_data = {}  # Dictionary to track flight data

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    # Map and DataFrame container
    html.Div([
        # Map container
        html.Div([
            dcc.Graph(id='live-map')
        ], style={'width': '100%', 'display': 'inline-block'}),

        # DataFrame container
        html.Div([
            DataTable(id='live-data-table',
                      columns=[{"name": i, "id": i} for i in previous_df.columns],
                      style_data_conditional=[
                          {'if': {'filter_query': '{status} = "addition"',
                                  'column_id': 'title'},
                           'backgroundColor': 'green',
                           'color': 'white'},
                          {'if': {'filter_query': '{status} = "removal"',
                                  'column_id': 'title'},
                           'backgroundColor': 'red',
                           'color': 'white'}
                      ],
                      sort_action='native',  # Enable sorting
                      sort_mode='multi',  # Allow multi-column sort
                      sort_by=[{'column_id': 'title', 'direction': 'asc'}])  # Default sort by title
        ], style={'width': '100%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

    # New DataTable for tracking entry/exit times and update counts
    html.Div([
        DataTable(id='tracking-table',
                  columns=[{"name": "Flight ID", "id": "flight_id"},
                           {"name": "Title", "id": "title"},
                           {"name": "Entry Time", "id": "entry"},
                           {"name": "Exit Time", "id": "exit"},
                           {"name": "Update Count", "id": "updates"}])
    ]),

    # Interval component for updating content
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    )
])

# Function to read data from CSV
def read_data_from_csv():
    global previous_df
    return generate_plane_movements(previous_df)

# Callback for updating the map
@app.callback(Output('live-map', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_map(n):
    global previous_df
    current_df = read_data_from_csv()

    fig = px.scatter_mapbox(
        current_df, 
        lat="lat", 
        lon="lon", 
        hover_name="title",
        hover_data=["plane_type", "timestamp"],
        color_discrete_sequence=["fuchsia"], 
        height=400)

    fig.update_layout(mapbox_style="open-street-map", 
                      mapbox_zoom=1, 
                      mapbox_center={"lat": 20, "lon": 0},  # Example center coordinates
                      uirevision='constant')

    return fig

# Helper function to update flight_data
def update_flight_tracking(current_df):
    global flight_data
    current_time = datetime.datetime.now()

    existing_titles = set([flight_id.split('_')[0] for flight_id in flight_data])
    new_titles = set(current_df['title']) - existing_titles

    # Update existing flights
    for title in existing_titles:
        if title in current_df['title'].values:
            flight_id = title + '_' + str(flight_data[title + '_last']['entry'])
            flight_data[flight_id]['updates'] += 1
            flight_data[flight_id]['exit'] = None

    # Add new and re-entered flights
    for title in new_titles:
        flight_id = title + '_' + str(current_time)
        flight_data[flight_id] = {'title': title, 'entry': current_time, 'exit': None, 'updates': 1}
        flight_data[title + '_last'] = {'entry': current_time}

    # Mark exit time for removed flights
    removed_titles = existing_titles - set(current_df['title'])
    for title in removed_titles:
        flight_id = title + '_' + str(flight_data[title + '_last']['entry'])
        flight_data[flight_id]['exit'] = current_time

# Callback for updating the DataFrame
@app.callback(Output('live-data-table', 'data'),
              [Input('interval-component', 'n_intervals')])
def update_table(n):
    global previous_df
    current_df = read_data_from_csv()

    if not previous_df.empty:
        # Identifying additions and removals
        current_df['status'] = ''
        current_df.loc[current_df['title'].isin(previous_df['title']), 'status'] = 'existing'
        current_df.loc[current_df['title'].isin(
            current_df[~current_df['title'].isin(previous_df['title'])]['title']), 'status'] = 'addition'
        previous_df['status'] = 'removal'
        combined_df = pd.concat([current_df, previous_df[~previous_df['title'].isin(current_df['title'])]])
    else:
        combined_df = current_df
        combined_df['status'] = 'existing'

    # Update flight tracking data
    update_flight_tracking(current_df)

    # Update the previous DataFrame
    previous_df = current_df.copy()

    return combined_df.sort_values('title').to_dict('records')

# New callback to update the tracking table
@app.callback(Output('tracking-table', 'data'),
              [Input('interval-component', 'n_intervals')])
def update_tracking_table(n):
    # Convert the tracking data to a DataFrame
    tracking_data = []
    for flight_id, data in flight_data.items():
        if '_last' not in flight_id:
            tracking_data.append({'flight_id': flight_id, **data})
    tracking_df = pd.DataFrame(tracking_data)
    return tracking_df.to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)

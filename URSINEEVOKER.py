import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash_table import DataTable
import pandas as pd
import plotly.express as px

from test_data import generate_plane_movements

# Global variable to store the previous state
previous_df = pd.DataFrame()
previous_df = generate_plane_movements(None)

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    # Map and DataFrame container
    html.Div([
        # Map container
        html.Div([
            dcc.Graph(id='live-map')
        ], style={'width': '50%', 'display': 'inline-block'}),

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
        ], style={'width': '50%', 'display': 'inline-block'})
    ], style={'display': 'flex', 'flex-direction': 'row'}),

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

    # Set the zoom level and center
    fig.update_layout(mapbox_style="open-street-map", 
                      mapbox_zoom=1, 
                      mapbox_center={"lat": 20, "lon": 0},  # Example center coordinates
                      uirevision='constant')

    return fig


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

    # Update the previous DataFrame
    previous_df = current_df.copy()

    return combined_df.sort_values('title').to_dict('records')

if __name__ == '__main__':
    app.run_server(debug=True)

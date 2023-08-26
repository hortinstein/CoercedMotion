import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import folium
import io
import plotly.express as px
import base64
import simplekml

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1("Upload CSV and Visualize Data"),
    dcc.Upload(
        id='upload-data',
        children=dbc.Button('Upload File', id='upload-button', n_clicks=0),
        multiple=False
    ),
    dbc.Row([
        dbc.Col(dbc.Button("Select All", id='select-all-button', n_clicks=0)),
        dbc.Col(dbc.Checklist(id='flight-selector', options=[], inline=True))
    ]),
    html.Div(id='map-output'),
    html.Div(id='gantt-output'),
    html.A("Download KML", id='download-link', download="flights.kml", href="", target="_blank")
])

@app.callback(
    Output('flight-selector', 'value'),
    Input('select-all-button', 'n_clicks'),
    State('flight-selector', 'options'),
    State('flight-selector', 'value')
)
def select_all_flights(n_clicks, options, values):
    # If all are already selected, deselect
    if n_clicks > 0 and len(values) == len(options):
        return []
    return [option['value'] for option in options]
@app.callback(
    Output('flight-selector', 'options'),
    Input('upload-data', 'contents')
)
def populate_checklist(contents):
    if contents is None:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = contents.split(',')
    decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
    df = pd.read_csv(decoded)
    return [{'label': f"Flight {num}", 'value': num} for num in df['flight_num']]

@app.callback([
    Output('map-output', 'children'),
    Output('gantt-output', 'children'),
    Output('download-link', 'href')
],
[Input('flight-selector', 'value')],
[State('upload-data', 'contents')]
)
def update_visualization(selected_flights, contents):
    if not contents or not selected_flights:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = contents.split(',')
    decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
    df = pd.read_csv(decoded)
    
    # Filter dataframe for selected flights
    df = df[df['flight_num'].isin(selected_flights)]

    # Create folium map
    m = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        folium.Marker(
            [row['src_lat'], row['src_lng']], 
            popup=f"From: {row['src_name']}\nFlight Number: {row['flight_num']}\nDeparture: {row['departure_date']}"
        ).add_to(m)
        folium.Marker(
            [row['dst_lat'], row['dst_long']], 
            popup=f"To: {row['dest_name']}\nFlight Number: {row['flight_num']}\nArrival: {row['arrival_date']}"
        ).add_to(m)
        folium.PolyLine([(row['src_lat'], row['src_lng']), (row['dst_lat'], row['dst_long'])], color="blue").add_to(m)
    m.save('map.html')

    # Create Gantt chart
    df['Start'] = pd.to_datetime(df['departure_date'])
    df['Finish'] = pd.to_datetime(df['arrival_date'])
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="flight_num", title="Flight Schedule Gantt Chart", hover_data=df.columns)

    # Create KML
    kml_content = generate_kml(df)
    kml_data_uri = "data:text/xml;charset=utf-8," + kml_content
    
    return html.Iframe(id='map', srcDoc=open('map.html', 'r').read(), width='100%', height='500'), dcc.Graph(figure=fig), kml_data_uri

def generate_kml(df):
    kml = simplekml.Kml()
    for _, row in df.iterrows():
        point_src = kml.newpoint(name=row['src_name'], coords=[(row['src_lng'], row['src_lat'])])
        point_dest = kml.newpoint(name=row['dest_name'], coords=[(row['dst_long'], row['dst_lat'])])
        linestring = kml.newlinestring(name=f"Flight {row['flight_num']}", coords=[(row['src_lng'], row['src_lat']), (row['dst_long'], row['dst_lat'])])
    
    return kml.kml()

if __name__ == '__main__':
    app.run_server(debug=True)

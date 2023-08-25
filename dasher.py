import dash
from dash import dcc, html
from dash.dependencies import Input, Output
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
    html.Div(id='map-output'),
    html.Div(id='gantt-output'),
    html.A("Download KML", id='download-link', download="flights.kml", href="", target="_blank")
])

@app.callback([
    Output('map-output', 'children'),
    Output('gantt-output', 'children'),
    Output('download-link', 'href')
],
    Input('upload-data', 'contents'))
def update_visualization(contents):
    if contents is None:
        raise dash.exceptions.PreventUpdate

    content_type, content_string = contents.split(',')
    decoded = io.StringIO(base64.b64decode(content_string).decode('utf-8'))
    df = pd.read_csv(decoded)

    # Create folium map
    m = folium.Map(location=[20, 0], zoom_start=2)
    for _, row in df.iterrows():
        folium.Marker([row['src_lat'], row['src_lng']], popup=f"From: {row['src_name']}").add_to(m)
        folium.Marker([row['dst_lat'], row['dst_long']], popup=f"To: {row['dest_name']}").add_to(m)
        folium.PolyLine([(row['src_lat'], row['src_lng']), (row['dst_lat'], row['dst_long'])], color="blue").add_to(m)
    m.save('map.html')

    # Create Gantt chart
    df['Start'] = pd.to_datetime(df['departure_date'])
    df['Finish'] = pd.to_datetime(df['arrival_date'])
    fig = px.timeline(df, x_start="Start", x_end="Finish", y="flight_num", title="Flight Schedule Gantt Chart")
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

import pandas as pd
import folium
import simplekml
from io import StringIO

df = pd.read_csv('./schedule.csv')

#df = pd.read_csv(StringIO('./schedule.csv'), parse_dates=['departure_date', 'arrival_date'])

# Convert string representation of datetime columns to ISO format while printing
df['departure_date'] = df['departure_date'].apply(lambda x: pd.to_datetime(x).isoformat())
df['arrival_date'] = df['arrival_date'].apply(lambda x: pd.to_datetime(x).isoformat())

print(df.head())
m = folium.Map()
m.save("footprint.html")


# Create a base map
m = folium.Map(location=[20,0], zoom_start=2)

# Visualize the data
for _, row in df.iterrows():
    folium.Marker([row['src_lat'], row['src_lng']], popup=f"From: {row['src_name']}").add_to(m)
    folium.Marker([row['dst_lat'], row['dst_long']], popup=f"To: {row['dest_name']}").add_to(m)
    folium.PolyLine([(row['src_lat'], row['src_lng']), (row['dst_lat'], row['dst_long'])], color="blue").add_to(m)

m.save('map.html')




# Create a KML file
kml = simplekml.Kml()

for _, row in df.iterrows():
    # Creating the description for the source point
    src_description = f"""
    Name: {row['src_name']}
    Departure Date: {row['departure_date']}
    Flight Number: {row['flight_num']}
    Weight: {row['weight']}
    Passengers: {row['passengers']}
    Cargo: {row['cargo_description']}
    """
    point = kml.newpoint(name=row['src_name'], coords=[(row['src_lng'], row['src_lat'])], description=src_description)

    # Creating the description for the destination point
    dest_description = f"""
    Name: {row['dest_name']}
    Arrival Date: {row['arrival_date']}
    Flight Number: {row['flight_num']}
    Weight: {row['weight']}
    Passengers: {row['passengers']}
    Cargo: {row['cargo_description']}
    """
    point = kml.newpoint(name=row['dest_name'], coords=[(row['dst_long'], row['dst_lat'])], description=dest_description)
    
    # Creating the description for the linestring (flight route)
    line_description = f"""
    Flight Number: {row['flight_num']}
    From: {row['src_name']}
    To: {row['dest_name']}
    Departure: {row['departure_date']}
    Arrival: {row['arrival_date']}
    Weight: {row['weight']}
    Passengers: {row['passengers']}
    Cargo: {row['cargo_description']}
    """
    linestring = kml.newlinestring(name=f"Flight {row['flight_num']}", coords=[(row['src_lng'], row['src_lat']), (row['dst_long'], row['dst_lat'])], description=line_description)

kml.save("flights.kml")

# Create the Markwhen File
with open("markwhen.md", "w") as f:
    f.write("## Flights\n")
   
    for _, row in df.iterrows():
        # f.write(f"---\ntitle: {row['flight_num']} - {row['src_name']} to {row['dest_name']}\nkey:\n  - entry\n---\n\n")
        f.write(f"{row['departure_date']}Z-{row['arrival_date']}Z: {row['flight_num']} - {row['src_name']} to {row['dest_name']}\n")
        f.write(f"[{row['src_name']}](location)\n")
        f.write(f"[{row['dest_name']}](location)\n")
        # f.write(f"### Flight {row['flight_num']}\n")
        # f.write(f"* From: {row['src_name']}\n")
        # f.write(f"* To: {row['dest_name']}\n")
        # f.write(f"* Departure: {row['departure_date']}\n")
        # f.write(f"* Arrival: {row['arrival_date']}\n")
        # f.write(f"* Weight: {row['weight']}\n")
        # f.write(f"* Passengers: {row['passengers']}\n")
        # f.write(f"* Cargo: {row['cargo_description']}\n")
        # f.write("\n")


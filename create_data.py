"""
Data source for entire project https://data.world/city-of-bloomington/
"""

import json
import psycopg2

with open("parking-areas.geojson") as f:
    data = json.load(f)


conn = psycopg2.connect(
    host="localhost",
    database="parkingdb",
    user="",
    password="",
)
cur = conn.cursor()

features = data["features"]
for idx, feature in enumerate(features):
    properties = feature["properties"]
    # Extract relevant data fields and store them in variables
    id = idx
    tag = properties["TAG"]
    geometry = feature["geometry"]
    # Perform any necessary data transformations or validations
    # Execute the SQL INSERT statement
    cur.execute(
        "INSERT INTO parking_app_parking (id, tag, geometry) VALUES (%s, %s, %s)",
        (id, tag, json.dumps(geometry)),
    )

conn.commit()
cur.close()
conn.close()

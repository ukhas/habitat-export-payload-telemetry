"""
Export Payload Telemetry
Adam Greig, Nov 2012
CouchDB List Functions

Format data for export in JSON and CSV formats, using the selected fields.
Used with the views:
    payload_telemetry/flight_payload_time
    payload_telemetry/payload_time
"""

import csv
import json
import StringIO
from couch_named_python import version


@version(4)
def json_list(head, req, rows):
    fields = req['query']['fields'].split(',')
    yield "[\n"
    comma = False
    for row in rows:
        if comma:
            yield ",\n"
        data = row['doc']['data']
        if "_receivers" in fields:
            data["_receivers"] = row['doc']['receivers'].keys()
        yield json.dumps(dict((k, data.get(k, '')) for k in fields))
        comma = True
    yield "\n]\n"


@version(6)
def csv_list(head, req, rows):
    yield req['query']['fields'] + "\n"
    fields = req['query']['fields'].split(',')
    for row in rows:
        data = row['doc']['data']
        if "_receivers" in fields:
            data["_receivers"] = ','.join(row['doc']['receivers'].keys())
        buf = StringIO.StringIO()
        writer = csv.writer(buf)
        writer.writerow([str(data.get(key, '')).strip() for key in fields])
        yield buf.getvalue()


@version(5)
def kml_list(head, req, rows):
    yield """<?xml version="1.0" encoding="UTF-8"?>
    <kml xmlns="http://earth.google.com/kml/2.0">
    <Document>
        <Style id="ept">
            <PolyStyle>
                <color>33ffffff</color>
            </PolyStyle>
        </Style>
        <Folder>
            <Placemark>
                <name>Track Segment</name>
                <styleUrl>#ept</styleUrl>
                <LineString>
                    <extrude>1</extrude>
                    <tessellate>1</tessellate>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>
    """
    launch = burst = land = name = None
    for row in rows:
        data = row['doc']['data']
        if not name:
            name = data['payload'] if 'payload' in data else "Unknown"
        if "latitude" in data and "longitude" in data and "altitude" in data:
            if not launch:
                launch = burst = data
            if data["altitude"] > burst["altitude"]:
                burst = data
            land = data
            yield "{longitude},{latitude},{altitude}\r\n".format(**data)
    launch_desc = ", ".join("{0}: {1}".format(k, v) for k, v in launch.items())
    burst_desc = ", ".join("{0}: {1}".format(k, v) for k, v in burst.items())
    land_desc = ", ".join("{0}: {1}".format(k, v) for k, v in land.items())
    launch_coords = "{longitude},{latitude},{altitude}\r\n".format(**launch)
    burst_coords = "{longitude},{latitude},{altitude}\r\n".format(**burst)
    land_coords = "{longitude},{latitude},{altitude}\r\n".format(**land)
    yield """
                    </coordinates>
                </LineString>
            </Placemark>
            <name>Flight Path</name>
        </Folder>
        <name>{name} Data Export</name>
        <Folder>
            <name>Launch, Burst and Landing Points</name>
            <Placemark>
                <name>Launch</name>
                <description>{launch_desc}</description>
                <Point>
                    <extrude>0</extrude>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>{launch_coords}</coordinates>
                </Point>
            </Placemark>
            <Placemark>
                <name>Burst</name>
                <description>{burst_desc}</description>
                <Point>
                    <extrude>0</extrude>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>{burst_coords}</coordinates>
                </Point>
            </Placemark>
            <Placemark>
                <name>Landing</name>
                <description>{land_desc}</description>
                <Point>
                    <extrude>0</extrude>
                    <altitudeMode>absolute</altitudeMode>
                    <coordinates>{land_coords}</coordinates>
                </Point>
            </Placemark>
        </Folder>
    </Document>
    </kml>""".format(**locals())

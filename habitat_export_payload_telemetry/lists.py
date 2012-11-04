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

@version(1)
def json_list(head, req, rows):
    fields = req['query']['fields'].split(',')
    yield "[\n"
    comma = False
    for row in rows:
        if comma:
            yield ",\n"
        data = row['doc']['data']
        yield json.dumps(dict((k, data.get(k, '')) for k in fields))
        comma = True
    yield "\n]\n"

@version(3)
def csv_list(head, req, rows):
    yield req['query']['fields'] + "\n"
    fields = req['query']['fields'].split(',')
    for row in rows:
        buf = StringIO.StringIO()
        writer = csv.writer(buf)
        data = row['doc']['data']
        writer.writerow([str(data.get(key, '')).strip() for key in fields])
        yield buf.getvalue()

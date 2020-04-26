import datetime
import os
import boto3
import requests
import csv
import json
from datetime import datetime
import dateutil
import pytz

def time2utc(time):
    # previously: datetime.now().isoformat()
    timestamp = time['s']
    timezone = time['tz']
    return dateutil.parser.parse("{}{}".format(timestamp, timezone)).astimezone(pytz.utc)

def mappingLankreisNameToKey():
    mapping = {}
    with open('schluessel_nuts_ags_kreise.csv', newline='', encoding='utf-8') as csvfile:
        fileReader = csv.reader(csvfile, delimiter=';', quotechar='|')
        header = next(fileReader)
        # Check file as empty
        if header is not None:
            # Iterate over each row after the header in the csv
            for row in fileReader:
                #nuts;ags;bez_nuts;schluessel_ags
                nuts = row[0]
                ags = int(row[1])
                bez_nuts = row[2]
                schluessel_ags = row[3]
                mapping[bez_nuts] = ags
    return mapping

def to_airquality(ags, lat, lon, response):
    data = response['data']
    date = time2utc(data['time'])
    return {
        'ags': ags,
        'datetime': date.strftime('%Y-%m-%dT%H:%M:%S'),
        'lat': lat,
        'lon': lon,
        'airquality': {
            'aqi': data['aqi'],
            'iaqi': data['iaqi']
        }
    }

airquality_token = os.environ['AIR_QUALITY_API_TOKEN']
bucket = []
mapping = mappingLankreisNameToKey()

with open('kreise_mit_center.csv', newline='', encoding='utf-8') as csvfile:
    fileReader = csv.reader(csvfile, delimiter=',', quotechar='|')
    header = next(fileReader)
    # Check file as empty
    if header is not None:
        # Iterate over each row after the header in the csv
        for row in fileReader:
            city_name = row[0]
            lon = row[1]
            lat = row[2]
            url = f'https://api.waqi.info/feed/geo:{lat};{lon}/?token={airquality_token}'
            response = requests.get(url)
            if response.status_code == 200 and response.json()['status'] == 'ok':
                airquality_record = to_airquality(mapping[city_name], lat, lon, response.json())
                # print(str(airquality_record).encode('utf-8'))
                bucket.append(airquality_record)

s3_client = boto3.client('s3')
date = datetime.now()

if len(bucket) > 0:
    response = s3_client.put_object(Body=json.dumps(bucket), Bucket='sdd-s3-bucket',
                                    Key='airquality/{}/{}/{}/{}'.format(str(date.year).zfill(4),
                                                                        str(date.month).zfill(2),
                                                                        str(date.day).zfill(2),
                                                                        str(date.hour).zfill(2)))
    print("Response: " + str(response))

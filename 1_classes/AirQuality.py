import datetime
import os
import requests
import csv
from datetime import datetime

import TimeTranformer
import MappingLandkreis

class AirQuality:
    def __init__(self, cityCode, latitude, longitude):
        self.ags = cityCode
        self.lat = latitude
        self.lon = longitude
        self.date = datetime.now()
        self.aqi = "-"
        self.iaqi = "-"
    def getUrl(self, token):
        return f'https://api.waqi.info/feed/geo:{self.lat};{self.lon}/?token={token}'
    def setData(self, response):
        data = response['data']
        self.date = TimeTranformer.time2utc(data['time'])
        self.aqi = data['aqi']
        self.iaqi = data['iaqi']
    def toJson(self):
        return {
            'ags': self.ags,
            'datetime': self.date.strftime('%Y-%m-%dT%H:%M:%S'),
            'lat': self.lat,
            'lon': self.lon,
            'airquality': {
                'aqi': self.aqi,
                'iaqi': self.iaqi
            }
        }

class AirQualityReader:
    def __init__(self, apiToken):
        self.airQualityApiToken = apiToken
        self.resetBucket()
        self.mapping = MappingLandkreis.mappingLankreisNameToKey()
    def resetBucket(self):
        self.bucket = []
    def readConfig(self, filename):
        self.cities = []
        with open(filename, newline='', encoding='utf-8') as csvfile:
            fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = next(fileReader)
            # Check file as empty
            if header is not None:
                # Iterate over each row after the header in the csv
                for row in fileReader:
                    self.cities.append({"cityName":row[0], "longitude":row[1], "latitude":row[2], "ags":self.mapping[row[0]]})
    def readAllData(self):
        for city in self.cities:
            self.readData(city)
    def readData(self, city):
        airquality_record = AirQuality(
            cityCode=city["ags"], 
            latitude=city["latitude"], 
            longitude=city["longitude"])
        response = requests.get(airquality_record.getUrl(self.airQualityApiToken))
        if response.status_code == 200 and response.json()['status'] == 'ok':
            airquality_record.setData(response.json())
            # print(str(airquality_record).encode('utf-8'))
            self.bucket.append(airquality_record.toJson())

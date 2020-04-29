import datetime
import os
import requests
import csv
from datetime import datetime

import TimeTranformer
import MappingLandkreis

class AirQuality:
    """ class to store single air quality dataset """
    def __init__(self, cityCode, latitude, longitude):
        """ Set basic data of the dataset: AGS, longitude, latitude """
        self.ags = cityCode
        self.lat = latitude
        self.lon = longitude
        self.date = datetime.now()
        self.aqi = "-"
        self.iaqi = "-"
    def setData(self, token):
        """ Get the data through the API with the API-token """
        url = f'https://api.waqi.info/feed/geo:{self.lat};{self.lon}/?token={token}'
        response = requests.get(url)
        if response.status_code == 200 and response.json()['status'] == 'ok':
            data = response.json()['data']
            self.date = TimeTranformer.time2utc(data['time'])
            self.aqi = data['aqi']
            self.iaqi = data['iaqi']
        else:
            print("Error in querying {}".format(url))
    def toJson(self):
        """ Convert the object to a JSON structure """
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
    """ Reader for AirQuality datasource """
    def __init__(self, apiToken=""):
        """ Constructor with API-token """
        self.airQualityApiToken = apiToken
        self.resetBucket()
        self.mapping = MappingLandkreis.mappingLankreisNameToKey()
    def resetBucket(self):
        """ Empty bucket """
        self.bucket = []
    def readConfig(self, filename):
        """ Read the configuration with the list of cities to collect """
        self.cities = []
        with open(filename, newline='', encoding='utf-8') as csvfile:
            fileReader = csv.reader(csvfile, delimiter=',', quotechar='"')
            header = next(fileReader)
            # Check file as empty
            if header is not None:
                # Iterate over each row after the header in the csv
                for row in fileReader:
                    if row[0] in self.mapping:
                        self.cities.append({"cityName":row[0], "longitude":row[1], "latitude":row[2], "ags":self.mapping[row[0]]})
                    else:
                        self.cities.append({"cityName":row[0], "longitude":row[1], "latitude":row[2], "ags":""})
    def readAllData(self):
        """ Collect data from all configured cities """
        for city in self.cities:
            if city["ags"]!="":
                self.readData(city)
    def readData(self, city):
        """ Collect single dataset for a given city """
        airquality_record = AirQuality(
            cityCode=city["ags"], 
            latitude=city["latitude"], 
            longitude=city["longitude"])
        airquality_record.setData(self.airQualityApiToken)
        self.bucket.append(airquality_record.toJson())

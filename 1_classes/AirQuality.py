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
        self._id = None
        self.name = None
        self.orgin = None
        self.aqi = "-"
        self.iaqi = "-"
    def setData(self, token):
        """ Get the data through the API with the API-token """
        url = f'https://api.waqi.info/feed/geo:{self.lat};{self.lon}/?token={token}'
        response = requests.get(url)
        if response.status_code == 200 and response.json()['status'] == 'ok':
            data = response.json()['data']
            self.date = TimeTranformer.time2utc(data['time'])
            try:
                self._id = data['idx']
            except:
                print(f"No idx for lat: {self.lat} lon: {self.lon}")
            try:
                self.name = data["city"]['name']
            except:
                print(f"No name for lat: {self.lat} lon: {self.lon}")
            try:
                self.orgin = data['city']["url"]
            except:
                print(f"No orgin for lat: {self.lat} lon: {self.lon}")
            try:
                self.time = data['time']["iso"]
            except:
                print(f"No time for lat: {self.lat} lon: {self.lon}")
            self.aqi = data['aqi']
            self.iaqi = data['iaqi']
        else:
            print("Error in querying {}".format(url))
    def toJson(self):
        """ Convert the object to a JSON structure """
        return {
            'ags': self.ags,
            'datetime': self.date.strftime('%Y-%m-%dT%H:%M:%S'),
            'time': self.time,
            'lat': self.lat,
            'lon': self.lon,
            'name': self.name,
            'orgin': self.orgin,
            '_id': self._id,
            'airquality': {
                'aqi': self.aqi,
                'iaqi': self.iaqi
            }
        }

class AirQualityReader:
    """ Reader for AirQuality datasource """
    def __init__(self, apiToken="", basePath="./"):
        """ Constructor with API-token """
        self.basePath = basePath
        self.airQualityApiToken = apiToken
        self.resetBucket()
        self.mapping = MappingLandkreis.mappingLankreisNameToKey(self.basePath)
    def resetBucket(self):
        """ Empty bucket """
        self.bucket = []
    def readConfig(self, filename):
        """ Read the configuration with the list of cities to collect """
        self.cities = []
        with open(self.basePath+filename, newline='', encoding='utf-8') as csvfile:
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
            if city["ags"] != "":
                self.readData(city)
    def readData(self, city):
        """ Collect single dataset for a given city """
        airquality_record = AirQuality(
            cityCode=city["ags"], 
            latitude=city["latitude"], 
            longitude=city["longitude"])
        airquality_record.setData(self.airQualityApiToken)
        self.bucket.append(airquality_record.toJson())


    def create_threads(self, num_th = 100):
        list_threads = []
        len_list_keys = len(self.cities)
        if len_list_keys > num_th:
            for id in range(1, num_th):
                list_sub = []
                thr = len_list_keys - len_list_keys * id / num_th
                while len(self.cities) > thr:
                    # print(len_list_keys)
                    x = self.cities.pop(0)
                    list_sub.append(x)
                list_threads.append(AWSRequest(list_sub, self.airQualityApiToken))
        else:
            list_threads.append(AWSRequest(self.cities))

        for t in list_threads:
            t.start()
        for t in list_threads:
            t.join()
        for t in list_threads:
            self.bucket += t.bucket

import threading
class AWSRequest(threading.Thread):
    def __init__(self, cities, airQualityApiToken):
        threading.Thread.__init__(self)
        self.cities = cities
        self.airQualityApiToken = airQualityApiToken
        self.bucket = []

    def read_data(self, city):
        airquality_record = AirQuality(
            cityCode=city["ags"],
            latitude=city["latitude"],
            longitude=city["longitude"])
        airquality_record.setData(self.airQualityApiToken)
        self.bucket.append(airquality_record.toJson())

    def run(self):
        for city in self.cities:
            if city["ags"] != "":
                self.read_data(city)
        return self.bucket


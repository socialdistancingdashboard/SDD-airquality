import sys
import os
sys.path.insert(0,"./")
import AirQuality
import S3

reader = AirQuality.AirQualityReader(apiToken=os.environ['AIR_QUALITY_API_TOKEN'])
reader.readConfig('0_config/kreise_mit_center.csv')
reader.readAllData()
S3.writeToAWS(reader.bucket)
import sys
import os
sys.path.insert(0,"./1_classes")

import AirQuality
import S3

reader = AirQuality.AirQualityReader(apiToken=os.environ['AIR_QUALITY_API_TOKEN'])
reader.readConfig('0_config/kreise_mit_center.csv')
reader.readAllData()
s3Handler = S3.S3_Handler()
s3Handler.writeToAWS("airquality", reader.bucket)

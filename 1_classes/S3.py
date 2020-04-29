from datetime import datetime
import boto3
import json

def writeToAWS(bucket):
    s3_client = boto3.client('s3')
    date = datetime.now()

    if len(bucket) > 0:
        response = s3_client.put_object(Body=json.dumps(bucket), Bucket='sdd-s3-bucket',
                                        Key='airquality/{}/{}/{}/{}'.format(str(date.year).zfill(4),
                                                                            str(date.month).zfill(2),
                                                                            str(date.day).zfill(2),
                                                                            str(date.hour).zfill(2)))
        print("Response: " + str(response))

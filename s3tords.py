from __future__ import print_function
import boto3
import logging
import os
import sys
import uuid
import pymysql
import csv
#import rds_config


rds_host  = 'flaskest.csjkhjjygutf.us-east-1.rds.amazonaws.com'
name = 'flask'
password = 'wizjysys'
db_name = 'flaskdb'


logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
except Exception as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to RDS mysql instance succeeded")

s3_client = boto3.client('s3')



    """
    Lambda handler
    """

def handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key'] 
    download_path = '/tmp/{}{}'.format(uuid.uuid4(), key)

    s3_client.download_file(bucket, key,download_path)

    csv_data = csv.reader(file(download_path))

    with conn.cursor() as cur:
        for idx, row in enumerate(csv_data):

            logger.info(row)
            try:
                cur.execute('INSERT INTO target_table(column1, column2, column3)' \
                                'VALUES("%s", "%s", "%s")'
                                , row)
            except Exception as e:
                logger.error(e)

            if idx % 100 == 0:
                conn.commit()

        conn.commit()

    return 'File loaded into RDS:' + str(download_path)

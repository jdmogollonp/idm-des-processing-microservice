import boto3
import logging
from boto3.session import Session
from botocore.exceptions import ClientError
import botocore
import io
import os
from typing import Union, BinaryIO
from datetime import datetime


logger = logging.getLogger(__name__)

aws_access_key_id="",
aws_secret_access_key=""

class S3Client:
    def __init__(self):
        self.client = boto3.client("s3",
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)        

    def download_file(self,bucket_name, object_name):
        """Download file from an S3 bucket
            :param bucket: Bucket to download from
            :param object_name: S3 object name. 
            :return: True if file was downloaded, else False          
        """
        s3 = boto3.resource('s3')

        try:
            s3.Bucket(bucket_name).download_file(object_name, f'data/{object_name}')
            return True
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                print("The object does not exist.")
                return False
            else:
                raise


    def upload_file(self,file_name, bucket, object_name=None):
        """Upload a file to an S3 bucket
            :param file_name: File to upload
            :param bucket: Bucket to upload to
            :param object_name: S3 object name. If not specified then file_name is used
            :return: True if file was uploaded, else False          
        """
        if object_name is None:
            object_name = os.path.basename(file_name)
        s3_client = boto3.client('s3')
        try:
            response = s3_client.upload_file(file_name, bucket, object_name)
            return response
        except ClientError as e:
            logging.error(e)
            return False
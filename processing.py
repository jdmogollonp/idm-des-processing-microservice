from storage_service import S3Client
from data_quality_service import Expectations
import os
import json

s3_client = S3Client()

class Process():
    def __init__(self,filename,bucket ):
        self.filename = filename
        self. bucket = bucket
        self.run()    
            
    def update_data_store(self):
        try:
            os.remove("data_store.json")
        except:
            pass
        details = {'filename': self.filename,
                  'bucket': self.bucket}
        with open('data_store.json', 'w') as convert_file:
             convert_file.write(json.dumps(details))
    
    def save_data(self):
        s3_client.download_file(self.bucket,self.filename)
        self.result = True

    def check_expectations(self):
        check  = Expectations(self.filename,self.bucket)
        check.run()
        
    def run(self):
        self.update_data_store()
        self.save_data()


class GenerateReport():
    def __init__(self,filename,bucket ):
        self.filename = filename
        self. bucket = bucket
        self.check_expectations()    
       
    def check_expectations(self):
        check  = Expectations(self.filename,self.bucket)
        check.run()

        
        


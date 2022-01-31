from storage_service import S3Client
from data_quality_service import Expectations
import os
import json
import shutil

s3_client = S3Client()


class Process():
    def __init__(self,filename,bucket ):
        self.filename = filename
        self. bucket = bucket
        self.run()
            
    def clear_folders(self):
        dir = 'data/' 
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))
      
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
        self.data_downloaded = True
        
    def check_expectations(self):
        check  = Expectations(self.filename,self.bucket)
        self.result = check.run()
        
    def run(self):
        #self.clear_folders()
        self.update_data_store()
        self.save_data()
        self.check_expectations()
        


import boto3   
import os

AWS_S3_BUCKET_NAME = 'microhive'
AWS_REGION = 'eu-west-2'
AWS_ACCESS_KEY = 'AKIAW5GFZFYMCOZ6FO4W'
AWS_SECRET_KEY = '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'

# LOCAL_FILE = 'paper1.json'
# NAME_FOR_S3 = 'paper1.json'

#function to connect to AWS using private key and access key AND upload Json file
def connect_aws(LOCAL_FILE, NAME_FOR_S3):
    try :
        s3_client = boto3.client(
            service_name='s3',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY
        )
        response = s3_client.upload_file(LOCAL_FILE, AWS_S3_BUCKET_NAME, NAME_FOR_S3)
        status = response.get("ResponseMetadata", {}).get("HTTPStatusCode") 
        if status == 200:
            print("Upload Successful")
    
        print(f'upload_log_to_aws response: {response}')

    except Exception as error :
        print(f"Connection to S3 bucket Failed {error}")
        

#function to upload multiple files
def upload_folder(local_folder) :                             #upload_folder('/Users/dipit.mahajan/Micro-Hive /Images', 'microhive')
    try:
        s3_client = boto3.client(
                service_name='s3',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY,
                aws_secret_access_key=AWS_SECRET_KEY
            )
        
        for root, dirs, files in os.walk(local_folder):
            for file in files:
                local_file_path = os.path.join(root, file)
                s3_file_path = os.path.relpath(local_file_path, local_folder)  # relative path for S3
                    
                    # Upload each file to S3 bucket
                s3_client.upload_file(local_file_path, AWS_S3_BUCKET_NAME, s3_file_path)

    except FileNotFoundError:
        print("The file was not found")








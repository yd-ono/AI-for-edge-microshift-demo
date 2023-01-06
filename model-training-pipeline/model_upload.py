from datetime import datetime
from os import environ

from boto3 import client


print('Reading environment variables.')

s3_access_key = environ.get('AWS_ACCESS_KEY_ID')
s3_secret_key = environ.get('AWS_SECRET_ACCESS_KEY')
s3_endpoint_url = environ.get('AWS_S3_ENDPOINT')
s3_bucket_name = environ.get('AWS_S3_BUCKET')

print(f'S3 access key: {s3_access_key}')
print(f'S3 secret key: {s3_secret_key}')
print(f'S3 endpoint URL: {s3_endpoint_url}')
print(f'S3 bucket name: {s3_bucket_name}')


def instantiate_s3_client():
    print('Instantiating S3 client.')
    s3_client = client(
        's3', endpoint_url=s3_endpoint_url,
        aws_access_key_id=s3_access_key, aws_secret_access_key=s3_secret_key
    )
    return s3_client


def get_target_object_name():
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    print(f'Current time stamp: {timestamp}.')
    s3_object_name = f'{timestamp}/model.data'
    return s3_object_name


def upload_model_package(s3_client, target_object_name):
    print(f'Uploading model package to {target_object_name} '
          f'in bucket {s3_bucket_name}.')
    with open('model.data', 'rb') as model_package_file:
        s3_client.upload_fileobj(
            model_package_file, s3_bucket_name, target_object_name
        )


if __name__ == '__main__':
    s3_client = instantiate_s3_client()
    target_object_name = get_target_object_name()
    upload_model_package(s3_client, target_object_name)
    print('Done.')

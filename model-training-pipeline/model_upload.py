from datetime import datetime

from boto3 import client

import s3_config


def instantiate_s3_client():
    print('Instantiating S3 client.')
    s3_client = client(
        's3',
        endpoint_url=s3_config.endpoint_url,
        aws_access_key_id=s3_config.access_key,
        aws_secret_access_key=s3_config.secret_key
    )
    return s3_client


def get_target_object_name():
    timestamp = datetime.now().strftime('%y%m%d%H%M')
    print(f'Current time stamp: {timestamp}.')
    s3_object_name = f'{timestamp}/model.data'
    return s3_object_name


def upload_model_package(s3_client, target_object_name):
    print(f'Uploading model package to {target_object_name} '
          f'in bucket {s3_config.bucket_name}.')
    with open('model.data', 'rb') as model_package_file:
        s3_client.upload_fileobj(
            model_package_file, s3_config.bucket_name, target_object_name
        )


if __name__ == '__main__':
    s3_client = instantiate_s3_client()
    target_object_name = get_target_object_name()
    upload_model_package(s3_client, target_object_name)
    print('Done.')

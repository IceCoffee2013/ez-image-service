import boto3
from boto3.s3.transfer import S3Transfer

bucket_name = 'ezswitch-image'


def s3_upload(data_path, save_path):
    client = boto3.client('s3')
    transfer = S3Transfer(client)

    # key = 'test-remote.jpg'
    # data_name = 'test.jpg'

    try:
        transfer.upload_file(data_path, bucket_name, save_path,
                             extra_args={'ACL': 'public-read'})
    except Exception:
        return

    file_url = '%s/%s/%s' % (client.meta.endpoint_url, bucket_name, save_path)

    print('URL:', file_url)
    return file_url

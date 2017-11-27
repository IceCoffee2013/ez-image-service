import boto3

# s3 = boto3.resource('s3')
#
# # Print out bucket names
# for bucket in s3.buckets.all():
#     print(bucket.name)
#
# # Upload a new file
# data = open('test.jpg', 'rb')
# s3.Bucket('ezswitch-bill').put_object(Key='test.jpg', Body=data)
from boto3.s3.transfer import S3Transfer

client = boto3.client('s3')
transfer = S3Transfer(client)

bucket = 'ezswitch-image'
key = 'test-remote.jpg'
data_name = 'test.jpg'
prefix_url = 'https://s3-ap-southeast-2.amazonaws.com'

transfer.upload_file(data_name, bucket, key,
                     extra_args={'ACL': 'public-read'})

file_url = '%s/%s/%s' % (prefix_url, bucket, key)

print('URL:', file_url)
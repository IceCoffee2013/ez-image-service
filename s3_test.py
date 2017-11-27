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

rr = transfer.upload_file(data_name, bucket, key,
                     extra_args={'ACL': 'public-read'})

print('rr', rr)

file_url = '%s/%s/%s' % (client.meta.endpoint_url, bucket, key)

print('URL:', file_url)
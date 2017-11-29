import boto3
from boto3.s3.transfer import S3Transfer
from flask import Flask, abort, request, send_from_directory
import shutil
import requests
import json
from imagelib.scan import CamImageScanner
from imagelib.errors.error import ContourNotFoundError, NotABillError
import logging
from logging.handlers import RotatingFileHandler
from time import strftime
import traceback

# Change PUBLIC DNS Name
# AWS_PUBLIC_DNS = "http://ec2-13-210-137-102.ap-southeast-2.compute.amazonaws.com"  # production environment
AWS_PUBLIC_DNS = "http://ec2-52-62-225-98.ap-southeast-2.compute.amazonaws.com"  # frank
ACCESS_ID = 'AKIAIUEFGZGHJ3QN5VFA'
ACCESS_KEY = 'v5KVifZ/H0FcCA5OEj6x/KBNCYTZyFV7+JeYQkfH'

bucket_name = 'ezswitch-image'
prefix_url = 'https://s3-ap-southeast-2.amazonaws.com'

app = Flask(__name__)

handler = RotatingFileHandler('./log/app.log', maxBytes=10000, backupCount=3)
logger = logging.getLogger('__name__')
logger.setLevel(logging.ERROR)
logger.addHandler(handler)


def download(url):
    fileNameExt = url.split("/")[-1]
    fPath = 'images/raw/' + fileNameExt
    response = requests.get(url, stream=True)
    with open(fPath, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    print("downloaded file")
    return fPath


@app.route('/api/imageOpt', methods=['POST'])
def imageOpt():
    if not request.json:
        abort(400)
    print("download image from: ", request.json['url'])
    # download image
    fileNameExt = download(request.json['url'])
    file = fileNameExt.split("/")[-1]
    print('images/processed/' + file)
    url = AWS_PUBLIC_DNS + '/images/processed/' + fileNameExt.split("/")[-1]
    cam = CamImageScanner(fileNameExt, 'images/processed/')

    img_host_path = 'images/processed/' + fileNameExt.split("/")[-1]
    img_remote_name = file.split('.')[0]

    try:
        cam.processImage()
    except ContourNotFoundError:
        return createResponse(400, {'err': 'fail to find edge'})
    try:
        cam.checkAndRotate()
        cam.checkAndRotate()
    except:
        url = s3_upload(img_host_path, file)
        return createResponse(400, {'err': 'Orientation Detection Fail, possibly not a bill', 'url': url})
    try:
        cam.validateBill()
    except NotABillError:
        url = s3_upload(img_host_path, file)
        return createResponse(400, {'err': 'not a bill', 'url': url})
    except Exception:
        url = s3_upload(img_host_path, file)
        return createResponse(400, {'err': 'ocr cmd error', 'url': url})
    # delete both images on server after s3 upload

    url = s3_upload(img_host_path, file)
    return createResponse(201, {'url': url})


@app.route('/api/hello')
def hello_world():
    return 'Hello, I am ezswitch image optimiser!'


def createResponse(statusCode, messageDict):
    return app.response_class(
        response=json.dumps(messageDict),
        status=statusCode,
        mimetype='application/json'
    )


@app.after_request
def after_request(response):
    # This IF avoids the duplication of registry in the log,
    # since that 500 is already logged via @app.errorhandler.
    if response.status_code != 500:
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.error('%s %s %s %s %s %s',
                     ts,
                     request.remote_addr,
                     request.method,
                     request.scheme,
                     request.full_path,
                     response.status)
    return response


@app.errorhandler(Exception)
def exceptions(e):
    ts = strftime('[%Y-%b-%d %H:%M]')
    tb = traceback.format_exc()
    logger.error('%s %s %s %s %s 5xx INTERNAL SERVER ERROR\n%s',
                 ts,
                 request.remote_addr,
                 request.method,
                 request.scheme,
                 request.full_path,
                 tb)
    return "Internal Server Error", 500


def s3_upload(data_path, save_path):
    # client = boto3.client('s3', aws_access_key_id=ACCESS_ID,
    #      aws_secret_access_key=ACCESS_KEY)
    client = boto3.client('s3')

    transfer = S3Transfer(client)

    try:
        transfer.upload_file(data_path, bucket_name, save_path,
                             extra_args={'ACL': 'public-read'})
    except Exception as e:
        print(e)
        ts = strftime('[%Y-%b-%d %H:%M]')
        logger.error('%s %s\n', ts, e)
        return

    file_url = '%s/%s/%s' % (prefix_url, bucket_name, save_path)

    print('URL:', file_url)
    return file_url


# run the app.
if __name__ == "__main__":
    # # The maxBytes is set to this number, in order to demonstrate the generation of multiple log files (backupCount).
    # handler = RotatingFileHandler('./log/app.log', maxBytes=10000, backupCount=3)
    # # getLogger('__name__') - decorators loggers to file / werkzeug loggers to stdout
    # # getLogger('werkzeug') - werkzeug loggers to file / nothing to stdout
    # logger = logging.getLogger('__name__')
    # logger.setLevel(logging.ERROR)
    # logger.addHandler(handler)
    # # app.debug = True

    app.run()

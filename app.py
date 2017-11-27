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
from utils import s3_upload

AWS_PUBLIC_DNS = "http://ec2-13-210-137-102.ap-southeast-2.compute.amazonaws.com"
app = Flask(__name__)


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
    print("download image from: " + request.json['url'])
    # download image
    fileNameExt = download(request.json['url'])
    file = fileNameExt.split("/")[-1]
    print('images/processed/' + file)
    url = AWS_PUBLIC_DNS + '/images/processed/' + fileNameExt.split("/")[-1]
    cam = CamImageScanner(fileNameExt, 'images/processed/')
    try:
        cam.processImage()
    except ContourNotFoundError:
        return createResponse(400, {'err': 'fail to find edge'})
    try:
        cam.checkAndRotate()
        cam.checkAndRotate()
    except:
        return createResponse(400, {'err': 'Orientation Detection Fail, possibly not a bill', 'url': url})
    try:
        cam.validateBill()
    except NotABillError:
        return createResponse(400, {'err': 'not a bill', 'url': url})
    except Exception:
        return createResponse(400, {'err': 'ocr cmd error', 'url': url})
    # delete both images on server after s3 upload
    url = AWS_PUBLIC_DNS + '/images/processed/' + fileNameExt.split("/")[-1]

    # s3_upload() TODO
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


# run the app.
if __name__ == "__main__":
    # The maxBytes is set to this number, in order to demonstrate the generation of multiple log files (backupCount).
    handler = RotatingFileHandler('./log/app.log', maxBytes=10000, backupCount=3)
    # getLogger('__name__') - decorators loggers to file / werkzeug loggers to stdout
    # getLogger('werkzeug') - werkzeug loggers to file / nothing to stdout
    logger = logging.getLogger('__name__')
    logger.setLevel(logging.ERROR)
    logger.addHandler(handler)
    # app.debug = True
    app.run()

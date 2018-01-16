import cv2

import requests
import shutil

from imagelib.errors.error import ContourNotFoundError, NotABillError
from imagelib.scan import CamImageScanner


def download(url):
    fileNameExt = url.split("/")[-1]
    fPath = 'images/raw/' + fileNameExt
    response = requests.get(url, stream=True)
    with open(fPath, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    # print("downloaded file")
    return fPath


def start(url, is_remote=True):
    if(is_remote):
        fileNameExt = download(url)
        file = fileNameExt.split("/")[-1]
        print('images/processed/' + file)
        url = '/images/processed/' + fileNameExt.split("/")[-1]
    else:
        fileNameExt = url
    cam = CamImageScanner(fileNameExt, 'images/processed/')

    try:
        cam.processImage()
    except ContourNotFoundError:
        print('fail to find edge')
    try:
        cam.checkAndRotate()
        cam.checkAndRotate()
    except Exception as e:
        print('err: Orientation Detection Fail, possibly not a bill', e)
    try:
        cam.validateBill()
    except NotABillError:
        print('not a bill', 'url', url)
    except Exception as e:
        print('ocr cmd error', e.args)


def check_size(raw_path, processed_path, ratio=0.4):
    # print(raw_path, processed_path)
    img1 = cv2.imread(raw_path)
    sp1 = img1.shape
    area1 = sp1[0] * sp1[1]
    img2 = cv2.imread(processed_path)
    sp2 = img2.shape
    area2 = sp2[0] * sp2[1]
    tmp_ratio = (area1 - area2) / area1
    print(sp1, area1, sp2, area2, tmp_ratio)
    if tmp_ratio < ratio:
        return False
    return True


name = '565-0.jpeg'
test_url1 = 'images/raw/' + name
test_url2 = 'images/processed/' + name
start(test_url1, False)
# checkSize(test_url1, test_url2)
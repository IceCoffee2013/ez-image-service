from imagelib.scan import CamImageScanner

name = 'bill1.jpg'
test_url1 = 'images/raw/' + name
test_url2 = 'images/processed/' + name

cam = CamImageScanner(test_url1, 'images/processed/')
# cam = CamImageScanner('test.jpg', 'tmp/')
cam.processImage()
result = cam.check_size(test_url1, test_url2)
print('result', result)
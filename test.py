from imagelib.scan import CamImageScanner

# cam = CamImageScanner('images/raw/fail1.jpg', 'images/processed/')
cam = CamImageScanner('test.jpg', 'tmp/')
cam.processImage()

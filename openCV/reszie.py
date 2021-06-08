import numpy as np
import cv2 as cv
img = cv.imread("D:\Code\MyCode\img\logo.png")
print(img.shape)
res = cv.resize(img,None,fx=2, fy=2, interpolation = cv.INTER_CUBIC)
print(res.shape)
#或者
height, width = img.shape[:2]
res = cv.resize(img,(2*width, 2*height), interpolation = cv.INTER_CUBIC)
print(res.shape)


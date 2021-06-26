import cv2
import numpy as np
img = cv2.imread("D:\Code\MyCode\img\lena.jpg")

imgInfo = img.shape
height = imgInfo[0]
width = imgInfo[1]




data = {
    "xmin":0 ,
    "xmax":150,
    "ymin":0 ,
    "ymax":100,
}
for m in range(data['ymin'],data['ymax']):
  for n in range(data['xmin'],data['xmax']):
    # pixel ->10*10
    if m%10 == 0 and n%10==0:
      for i in range(0,10):
        for j in range(0,10):
          (b,g,r) = img[m,n]
          img[i+m,j+n] = (b,g,r)
cv2.imshow('dst',img)
cv2.waitKey(0)
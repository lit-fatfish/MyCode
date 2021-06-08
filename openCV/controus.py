import numpy as np
import cv2 as cv
import cv2

img = cv.imread("D:\Code\MyCode\img\logo.png")
imgray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
ret, thresh = cv.threshold(imgray, 50, 255, 0)
contours, hierarchy = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

print(len(contours))
print(contours)
# 绘制所有的轮廓-1 ，绘制单个轮廓，根据需要
cv.drawContours(img, contours, -1, (0,255,0), 3)

# 获取轮廓的位置和长宽
x,y,w,h = cv.boundingRect(contours[1])
print(x,y,w,h)
img = cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),3)
cv2.imshow("res", img)



cv.waitKey(0)
cv2.destroyAllWindows()
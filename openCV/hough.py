import cv2
import cv2 as cv
import numpy as np
import time



img = cv2.imread(r'D:\Code\MyCode\img\board_RB_2_2021012320574183.jpg')

img2gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


ret, thresh = cv2.threshold(img2gray, 127, 255, cv2.THRESH_BINARY)
lines = cv2.HoughLines(thresh, 1, np.pi/180, 118)
print(len(lines))


edges = cv2.Canny(img, 50, 150, apertureSize=3)
time_now = time.time()

lines = cv2.HoughLines(edges, 1, np.pi/180, 118)
print(time.time() - time_now)
print(len(lines))

# 概论霍夫 
time_now = time.time()
lines = cv.HoughLinesP(edges,1,np.pi/180,100,minLineLength=100,maxLineGap=10)
print(time.time() - time_now)
print(len(lines))

cv2.imshow("edges", edges)
cv2.imshow("thresh", thresh)




cv.waitKey(0)
cv2.destroyAllWindows()
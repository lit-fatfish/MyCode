import cv2 as cv
import cv2
import numpy as np

img = cv2.imread("D:\Code\MyCode\img\logo.png")

hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)

"""
其中蓝色logo的值为[105 255 221]  一般选择±10左右的范围
红色为：[[[  1 229 231]]]
"""

# 定义HSV中蓝色的范围
lower_blue = np.array([100,50,50])
upper_blue = np.array([130,255,255])

mask_blue = cv.inRange(hsv, lower_blue, upper_blue)

# 定义HSV中红色的范围
lower_blue = np.array([0,50,50])
upper_blue = np.array([20,255,255])

mask_red = cv.inRange(hsv, lower_blue, upper_blue)

mask = mask_blue + mask_red  # 已经根据需要筛选后的二值化图片

res = cv.bitwise_and(img,img, mask= mask)

cv2.imshow("img", img)
cv2.imshow("mask", mask)
cv2.imshow("res", res)



cv.waitKey(0)
cv2.destroyAllWindows()
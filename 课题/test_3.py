import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils

# 3.光伏组件分割

min_thresh = 56
min_side_len = int(360/3) 
min_side_num = 3
min_poly_len = int(360/12)

img = cv2.imread("./src_file/pv.jpg")

print(img.shape)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转灰度图
cv2.imwrite("./dst_file/pv_gray.jpg", gray)

hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  # 转hsv

# 二值化
# ret, otsu_img = cv2.threshold(gray,104,255, cv2.THRESH_BINARY)
ret, otsu_img = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)
# blur = cv2.GaussianBlur(gray,(5,5),0)
# ret3,otsu_img = cv2.threshold(blur,0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

cv2.imshow("otsu_img", otsu_img)
cv2.imwrite("./dst_file/pv_binary.jpg", otsu_img)


# kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
# otsu_img = cv2.morphologyEx(otsu_img, cv2.MORPH_CLOSE, kernel)


# 膨胀
# kernel = np.ones((1, 1), np.uint8)
# otsu_img = cv2.dilate(otsu_img, kernel)

# cv2.imshow("close", otsu_img)


# 腐蚀
kernel = np.ones((50, 50), np.uint8)
dst = cv2.erode(otsu_img, kernel)
cv2.imshow("erode", dst)

# 膨胀
kernel = np.ones((30, 30), np.uint8)
dst = cv2.dilate(dst, kernel)


cv2.imshow("dilate", dst)


contours, hierarchy = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 轮廓检测
approxs = [cv2.approxPolyDP(cnt, min_side_len, True) for cnt in contours]  # 填充数据
# approxs = [cv2.approxPolyDP(cnt,  0.1*cv2.arcLength(cnt,True), True) for cnt in contours]  # 填充数据

boxes = [cv2.boundingRect(c) for c in contours]
for box in boxes:
    x, y, w, h = box
    #绘制矩形框对轮廓进行定位
    cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 2)



approxs = [approx for approx in approxs                             
            if len(approx) > min_side_num and cv2.arcLength(approx, True) > min_poly_len]# 只取满足条件的框
contours = approxs

new_black_img = np.zeros(img.shape)


poly_img =  cv2.polylines(new_black_img, contours, True, (255, 255, 255), 2)



cv2.imshow("poly_img", poly_img)


# blur = cv2.GaussianBlur(hsv_img,(5,5),0)
# ret3,th3 = cv2.threshold(blur,0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

# ret, th3 = cv2.threshold(hsv_img, 0, 255, cv2.THRESH_OTSU)

#设定颜色HSV范围，假定为红色
# redLower = np.array([156, 43, 46])
# redUpper = np.array([179, 255, 255])


# #==============指定蓝色值的范围================
# min_blue = np.array([110,50,50])
# max_blue = np.array([130,255,255])

# min_blue = np.array([0,43,46])
# max_blue = np.array([180,255,255])

# #去除颜色范围外的其余颜色
# mask = cv2.inRange(hsv_img, redLower, redUpper)
# mask_blue = cv2.inRange(hsv_img, min_blue, max_blue)
# # cv2.imshow("mask", mask)

# # 通过掩码控制的按位与运算，锁定蓝色区域
# blue = cv2.bitwise_and(img, img, mask=mask_blue)
# cv2.imshow("blue", blue)


cv2.imshow("img", img)
cv2.imwrite("./dst_file/pv_img.jpg", img)
# cv2.imshow("HSV", hsv_img)
# cv2.imshow("th3", th3)

cv2.waitKey()
cv2.destroyAllWindows()
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils

# 对以下图片红框部分做二值化，分别用绝对值，全局均值，大津律之、直方图双峰法，选取阈值。
# 二值化-为了选取目标。 筛选你需要的信息
img = cv2.imread("./src_file/2.jpg")

print(img.shape)

board_arr = {
    "xmin": 805,
    "ymin": 427,
    "xmax": 1128,
    "ymax": 672,
}

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
board_area = img_gray[board_arr["ymin"]:board_arr["ymax"], board_arr["xmin"]:board_arr["xmax"]]


# 绝对值二值化-阈值127
# mask = board_area > 127
abs_img = board_area.copy() 
abs_img[abs_img > 127] = 255
abs_img[abs_img <= 127] = 0
cv2.imwrite("./dst_file/2_abs.jpg", abs_img)


# 全局均值-阈值127
binary_img = board_area.copy()
ret, binary_img = cv2.threshold(binary_img,127,255, cv2.THRESH_BINARY)
cv2.imwrite("./dst_file/2_binary.jpg", binary_img)


# 大津律值法
otsu_img = board_area.copy()
ret, otsu_img = cv2.threshold(otsu_img, 0, 255, cv2.THRESH_OTSU)
cv2.imwrite("./dst_file/2_otsu.jpg", otsu_img)



# 直方图双峰法
# 高斯滤波后再采用Otsu阈值
blur = cv2.GaussianBlur(board_area,(5,5),0)
ret3,th3 = cv2.threshold(blur,0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite("./dst_file/2_otsu_gauss.jpg", th3)

# 
img = cv2.rectangle(img, (board_arr['xmin'], board_arr['ymin']), (board_arr['xmax'], board_arr['ymax']), (0,255,0), 2)


cv2.imshow("test", img)
cv2.imshow("abs_img", abs_img)
cv2.imshow("binary_img", binary_img)
cv2.imshow("otsu_img", otsu_img)
cv2.imshow("th3", th3)

cv2.imwrite("./dst_file/2_img.jpg", img)


# plt.hist(binary_img.ravel(), 256)
# plt.hist(otsu_img.ravel(), 256)

# plt.hist(th3.ravel(), 256)

plt.show()

cv2.waitKey()
cv2.destroyAllWindows()
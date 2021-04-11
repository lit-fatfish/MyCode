import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils

# 5.找出下图的白板轮廓



img = cv2.imread("./src_file/4.jpg")

print(img.shape)
min_thresh = 56
min_side_len = int(360/24) 
min_side_num = 5 
min_poly_len = int(360/12)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 转灰度图
ret, thresh = cv2.threshold(gray, min_thresh, 255, 0)  # 二值化
# thresh = cv2.GaussianBlur(thresh, (9, 9), 0)  # 高斯模糊

contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 轮廓检测
approxs = [cv2.approxPolyDP(cnt, min_side_len, True) for cnt in contours]  # 填充数据

approxs = [approx for approx in approxs                             
            if len(approx) > min_side_num and cv2.arcLength(approx, True) > min_poly_len]# 只取满足条件的框
contours = approxs

new_black_img = np.zeros(img.shape)


poly_img =  cv2.polylines(new_black_img, contours, True, (255, 255, 255), 2)
cv2.imwrite("./dst_file/5_poly.jpg", poly_img)


plt.show()

cv2.imshow("test", img)
cv2.imshow("approxs", poly_img)



cv2.waitKey()
cv2.destroyAllWindows()
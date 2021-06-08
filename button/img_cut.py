import cv2,os,sys
import numpy as np

"""
需求：
    1、输入一张图片
    2、找出纽扣的轮廓，并且框出来，或者裁切？
    3、保存图片
"""

img_src_path = r"D:\Code\MyCode\button\src_img"
img_dst_path = r"D:\Code\MyCode\button\dst_img"


listdir = os.listdir(img_src_path)

min_side_len = int(360/24) 


for index,item in enumerate(listdir):
    img_full_path = os.path.join(img_src_path, item)
    if not os.path.exists(img_full_path):
        continue
    
    img = cv2.imread(img_full_path)
    if img is None:
        continue
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 大津律值法
    ret, otsu_img = cv2.threshold(img_gray, 0, 255, cv2.THRESH_OTSU)
    
    cv2.imwrite(os.path.join(img_dst_path, "otsu_" + item), otsu_img)

    # 腐蚀
    # kernel = np.ones((9, 9), np.uint8)
    # dst = cv2.erode(otsu_img, kernel)

    # 膨胀
    kernel = np.ones((9, 9), np.uint8)
    dst = cv2.dilate(otsu_img, kernel)
    cv2.imwrite(os.path.join(img_dst_path, "dilate_" + item), dst)

    # 找轮廓
    contours = cv2.findContours(dst, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    print(contours)
    approxs = [cv2.approxPolyDP(cnt, min_side_len, True) for cnt in contours]  # 填充数据


    # approxs = [cv2.approxPolyDP(cnt, 0.1*cv2.arcLength(cnt, True), True) for cnt in contours]
    # approxs = [cv2.approxPolyDP(cnt, min_side_len, True) for cnt in contours]


    # print(approxs)
    # poly_img =  cv2.polylines(dst, contours, True, (255, 255, 255), 2)
    # cv2.imwrite(os.path.join(img_dst_path, "contours_" + item), dst)









    








## 目的输入图片的地址，然后生成一个图片
'''
输入：一张图片和框选的位置
输出：一张新的图片
    框，黑度占比，等级，

'''

import cv2, os
import numpy as np


# img_path = "/home/anlly/workspace/nas_project/frank/Code/2021年1月25日/img/line1/1/close.jpg"
# img_path = "/home/anlly/workspace/nas_project/frank/Code/2021年1月25日/img/line1/1/middle.jpg"
img_path = "/home/anlly/workspace/nas_project/frank/Code/2021年1月25日/img/line1/1/remote.jpg"

# img_path = "/home/anlly/workspace/nas_project/frank/Code/2021年1月25日/img/横向/1/1.jpg"


index = img_path.rfind('/')
dst_path = img_path[:index+1] + "erode_new_" + img_path[index+1:]
thresh_path = img_path[:index+1] + "dajin_thresh_" + img_path[index+1:]
erode_path = img_path[:index+1] + "erode_" + img_path[index+1:]


rec = {'xmin': 1239, 'ymin': 693, 'xmax': 1407, 'ymax': 852}
# rec = {
#   "xmin": 1204,
#   "ymin": 1066,
#   "xmax": 1438,
#   "ymax": 1307
# }

binarization_thres = 0.5



# cv2.imwrite("new_rect.jpg", rect_img)

# standard_level = int(img_path[68-2:68-1]) * 0.2
standard_level = 0.2
# print("standard_level", standard_level)

# for i in range(80):
frame = cv2.imread(img_path)

# print(len(frame))

# 裁剪框内的区域
rect_img = frame[rec['ymin']:rec['ymax'], rec['xmin']:rec['xmax']]
# binarization_thres += 0.01
# 转为灰度图
rect_img = cv2.cvtColor(rect_img, cv2.COLOR_BGR2GRAY)
# 二值化， 大津法
ret, binary = cv2.threshold(rect_img, 0, 255, cv2.THRESH_OTSU)
rect_img = binary
# rect_img[rect_img > 255*binarization_thres] = 255
# rect_img[rect_img <= 255*binarization_thres] = 0
cv2.imwrite("thresh.jpg", rect_img)

kernel = np.ones((1,1), np.uint8)

rect_img = cv2.erode(rect_img, kernel)
cv2.imwrite(erode_path, rect_img)


rect_img_h, rect_img_w = rect_img.shape
lingerman_blackness = np.sum(rect_img == 0) / (rect_img_h * rect_img_w)
lingerman_blackness = round(lingerman_blackness, 3)

level = round(lingerman_blackness / standard_level, 2)
# print(level)
# if level > 1.99 and level <= 2.08:
#   break
# print("thresh", binarization_thres)
print("lingerman_blackness", lingerman_blackness)
print("level", level)
print(rec)


# 画框
frame = cv2.rectangle(frame, (rec['xmin'], rec['ymin']), (rec['xmax'], rec['ymax']), (0,0,255), 2)

frame = cv2.putText(frame, "blackness: " + str(lingerman_blackness), ( 0, 350), cv2.FONT_HERSHEY_SIMPLEX, 4,[0,0,255], 4)
frame = cv2.putText(frame, "level: " + str(level), ( 0, 450), cv2.FONT_HERSHEY_SIMPLEX, 4,[0,0,255], 4)
# frame = cv2.putText(frame, "thresh: " + str(binarization_thres), ( 0, 550), cv2.FONT_HERSHEY_SIMPLEX, 4,[0,0,255], 4)


cv2.imwrite(thresh_path, rect_img)
cv2.imwrite(dst_path, frame)

# cv2.imwrite("new.jpg", frame)




















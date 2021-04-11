import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils

# 4.对下面图片中的白板进行开运算和闭运算
img = cv2.imread("./src_file/3.jpg")

print(img.shape)

board_arr = {
    "xmin": 316,
    "ymin": 296,
    "xmax": 714,
    "ymax": 682,
}

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
board_area = img_gray[board_arr["ymin"]:board_arr["ymax"], board_arr["xmin"]:board_arr["xmax"]]

blur = cv2.GaussianBlur(board_area,(5,5),0)
ret3,th3 = cv2.threshold(blur,0,255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
cv2.imwrite("./dst_file/4_threshold.jpg", th3)


# 开运算 去噪
# kernel = np.ones((5, 5), np.uint8)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(15,15))
opening = cv2.morphologyEx(th3, cv2.MORPH_OPEN, kernel)
cv2.imwrite("./dst_file/4_opening.jpg", opening)


# 闭运算 
kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))
closing= cv2.morphologyEx(th3, cv2.MORPH_CLOSE, kernel)
cv2.imwrite("./dst_file/4_closing.jpg", closing)


img = cv2.rectangle(img, (board_arr['xmin'], board_arr['ymin']), (board_arr['xmax'], board_arr['ymax']), (0,255,0), 2)

cv2.imwrite("./dst_file/4_img.jpg", img)

plt.show()

cv2.imshow("test", img)
cv2.imshow("th3", th3)
cv2.imshow("opening", opening)
cv2.imshow("closing", closing)

cv2.waitKey()
cv2.destroyAllWindows()
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils
# 1.1对单帧图片红框部分进行灰度处理，白板的区域自己用坐标标定，在黄框部分画出直方图

utils = Utils()

img = cv2.imread("./src_file/1.1.jpg")

img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


board_arr = {
    "xmin": 1313,
    "ymin": 370,
    "xmax": 1683,
    "ymax": 723,
}

board_area = img_gray[board_arr["ymin"]:board_arr["ymax"], board_arr["xmin"]:board_arr["xmax"]]


hist_board = cv2.calcHist([board_area],[0], None, [256], [0, 256])

img = utils.draw_axis(img, hist_board, (85, 1020), [], int(max(hist_board)))

img[0:board_area.shape[0], img.shape[1]-board_area.shape[1]-50:img.shape[1]-50] = cv2.cvtColor(board_area, cv2.COLOR_GRAY2BGR)

plt.plot(hist_board)


# cv2.imshow("test1", img_gray)
# cv2.imshow("test2", board_area)
cv2.imshow("test", img)

cv2.imwrite("./dst_file/1.1.jpg", img)
plt.show()

cv2.waitKey()
cv2.destroyAllWindows()
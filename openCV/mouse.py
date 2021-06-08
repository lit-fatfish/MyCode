# openCV 鼠标事件

import numpy as np
import cv2 as cv
# 鼠标回调函数
def draw_circle(event,x,y,flags,param):
    if event == cv.EVENT_LBUTTONDBLCLK:
        cv.circle(img,(x,y),100,(255,0,0),-1)
# 创建一个黑色的图像，一个窗口，并绑定到窗口的功能

def piex_print(event,x,y,flags,param):
    if event == cv.EVENT_LBUTTONDOWN:
        print(img[x,y])
        piex = img[x,y]
        piex = np.uint8([[piex]])
        hsv = cv.cvtColor(piex, cv.COLOR_BGR2HSV)
        print(hsv)

# img = np.zeros((512,512,3), np.uint8)
img = cv.imread("D:\Code\MyCode\img\logo.png")
cv.namedWindow('image')
# cv.setMouseCallback('image',draw_circle)
cv.setMouseCallback('image',piex_print)


while(1):
    cv.imshow('image',img)
    if cv.waitKey(20) & 0xFF == 27:
        break
cv.destroyAllWindows()

import cv2 as cv


img2 = cv.imread(r'D:\Code\MyCode\img\logo.png')
img1 = cv.imread(r'D:\Code\MyCode\img\lena.jpg')
# 我想把logo放在左上角，所以我创建了ROI

img2 = cv.resize(img2, (200,100))
rows,cols,channels = img2.shape
roi = img1[0:rows, 0:cols ]
# 现在创建logo的掩码，并同时创建其相反掩码
img2gray = cv.cvtColor(img2,cv.COLOR_BGR2GRAY)
ret, mask = cv.threshold(img2gray, 10, 255, cv.THRESH_BINARY)
cv.imshow('mask',mask)
mask_inv = cv.bitwise_not(mask)
cv.imshow('mask_inv',mask_inv)
# 现在将ROI中logo的区域涂黑
img1_bg = cv.bitwise_and(roi,roi,mask = mask_inv)
cv.imshow('img1_bg',img1_bg)
# 仅从logo图像中提取logo区域
img2_fg = cv.bitwise_and(img2,img2,mask = mask)
cv.imshow('img2_fg',img2_fg)
# 将logo放入ROI并修改主图像
dst = cv.add(img1_bg,img2_fg)
cv.imshow('dst',dst)

img1[0:rows, 0:cols ] = dst
cv.imshow('res',img1)
cv.waitKey(0)
cv.destroyAllWindows()
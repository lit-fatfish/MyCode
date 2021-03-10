import cv2
import numpy as np


def rotate_bound(image, angle):
    # grab the dimensions of the image and then determine the
    # center
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    # (i.e., the rotation components of the matrix)
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY
    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))

img = cv2.imread("img/lena.jpg")


# rotate = rotate_bound(img, 5)

# cv2.imshow("rotate.jpg", rotate)
#1. 左右镜像，水平翻转
new_img = cv2.flip(img, 1)
cv2.imshow("flip_1", new_img)

#2. 上下镜像，垂直翻转
new_img = cv2.flip(img, 0)
cv2.imshow("flip_0", new_img)


#3. 上下左右镜像，垂直翻转  + 水平翻转
new_img = cv2.flip(img, -1)
cv2.imshow("flip_-1", new_img)

# 4.转置
trans_img = cv2.transpose(img)
cv2.imshow("transpose", trans_img)
# 5.顺时针旋转90度
clockwise_img = cv2.flip(trans_img, 1)

# 6.逆时针旋转90度
anti_clockwise_img = cv2.flip(trans_img, 0)

cv2.imshow("anti_clockwise_img_90", anti_clockwise_img)

cv2.imshow("clockwise_90", clockwise_img)

cv2.waitKey(0)

import cv2, os
import numpy as np



img = cv2.imread("D:\Code\MyCode\img\lena.jpg", 0)

r,c = img.shape


mask = np.zeros((r,c), dtype=np.uint8)


data = {
    "xmin":0 ,
    "xmax":150,
    "ymin":0 ,
    "ymax":100,
}

mask[data['xmin']:data['xmax'], data['ymin']:data['ymax']] = 1
key = np.random.randint(0, 256, size=[r,c ], dtype=np.uint8)

lenaXorKey=cv2.bitwise_xor(img, key)

encryptFace=cv2.bitwise_and (lenaXorKey, mask*255)

noFace1 = cv2.bitwise_and(img, (1-mask) * 255)


maskFace = encryptFace + noFace1



cv2.imshow("maskFace", maskFace)


cv2.waitKey(0)

cv2.destroyAllWindows()

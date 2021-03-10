import cv2
import numpy as np
import matplotlib.pyplot as plt


img = cv2.imread("D:\Code\MyCode\img\lena.jpg")

# img = np.zeros((100,100))
# cv2.imshow("original", img)

plt.hist(img.ravel(), 256)


## cv2.calcHist
histb = cv2.calcHist([img], [0], None, [256], [0,255])
histg = cv2.calcHist([img], [1], None, [256], [0,255])
histr = cv2.calcHist([img], [2], None, [256], [0,255])
plt.plot(histb, color='b')
plt.plot(histg, color='g')
plt.plot(histr, color='r')

plt.show()


cv2.waitKey()
cv2.destroyAllWindows()


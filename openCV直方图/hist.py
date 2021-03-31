#encoding:utf-8
import cv2
import numpy as np
import matplotlib.pyplot as plt
 
src = cv2.imread(r'D:\Code\MyCode\img\lena.jpg ')
cv2.imshow("src", src)

src = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)

# cv2.imshow("src", src)
 
# plt.hist(src.ravel(), 256)
# plt.show()
 
hist = cv2.calcHist([src], [0], None, [256], [0, 256])

plt.plot(hist)
plt.savefig("histr.jpg")

plt.show()

# cv2.imwrite("hist.jpg", hist)

cv2.waitKey(0)
cv2.destroyAllWindows()
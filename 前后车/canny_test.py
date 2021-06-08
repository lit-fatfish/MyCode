import cv2
import numpy as np

img = cv2.imread(r'D:\Code\MyCode\img\wallpaper5.jpg', 0)


print(img.shape)



canny = cv2.Canny(img, 100, 200)

print(canny)

cv2.imshow("img", img)

cv2.imshow("canny", canny)
print(canny.shape)

sum1 = np.sum(canny > 1)

print(sum1)
cv2.waitKey()
cv2.destroyAllWindows()




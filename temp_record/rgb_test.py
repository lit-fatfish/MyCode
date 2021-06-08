import cv2
import numpy as np


img = cv2.imread(r'D:\Code\MyCode\img\z_rect_img.jpg')


rgb_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

bgr_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

diff_img = rgb_img - bgr_img
print(diff_img, diff_img)



print("rgb_img", rgb_img)
print("bgr_img", bgr_img)

ret, otsu_img = cv2.threshold(bgr_img, 0, 255, cv2.THRESH_OTSU)
print(otsu_img)

otsu_img_arr = otsu_img
otsu_img_16 = np.array(otsu_img, dtype='int16')


mask = np.ones(otsu_img.shape, dtype='uint8')

otsu_img_mask = cv2.bitwise_and(otsu_img, mask)

print(mask)
print(otsu_img_mask)

cv2.imshow("rgb_img", rgb_img)
cv2.imshow("bgr_img", bgr_img)
cv2.imshow("diff_img", diff_img)
cv2.imshow("otsu_img", otsu_img)
cv2.imshow("otsu_img_mask", otsu_img_mask)


cv2.waitKey()


cv2.destroyAllWindows()


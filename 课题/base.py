import cv2


img = cv2.imread("./src_file/1.1.jpg")

print(img.shape)

cv2.imshow("test", img)


cv2.waitKey()
cv2.destroyAllWindows()
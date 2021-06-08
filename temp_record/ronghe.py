import cv2

img1 = cv2.imread(r'D:\Code\MyCode\img\lena.jpg')
img2 = cv2.imread(r'D:\Code\MyCode\img\wallpaper5.jpg')

img1 = cv2.resize(img1, (200, 200))

img2 = cv2.resize(img2, (200, 200))

dst = cv2.addWeighted(img1,0.7,img2,0.3,0)

cv2.imshow('dst',dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
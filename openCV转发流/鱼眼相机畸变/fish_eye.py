# 根据之前获取到的k,d值，将一张图片进行畸变校准
'''
DIM=(640, 480)
K=np.array([[196.31562552201345, 0.0, 306.8391875928363], [0.0, 196.05769001405187, 263.06516965475646], [0.0, 0.0, 1.0]])
D=np.array([[0.3035798469765248], [0.014563430886205675], [-0.09521207109577143], [0.03515452469547106]])
'''
import numpy as np
import cv2,sys


# DIM=XXX
# K=np.array(YYY)
# D=np.array(ZZZ)
DIM=(640, 480)
K=np.array([[196.31562552201345, 0.0, 306.8391875928363], [0.0, 196.05769001405187, 263.06516965475646], [0.0, 0.0, 1.0]])
D=np.array([[0.3035798469765248], [0.014563430886205675], [-0.09521207109577143], [0.03515452469547106]])
def undistort(img_path):
  img = cv2.imread(img_path)
  h,w = img.shape[:2]
  map1, map2 = cv2.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, DIM, cv2.CV_16SC2)
  undistorted_img = cv2.remap(img, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
  cv2.imwrite("undistorted.jpg", undistorted_img)
if __name__ == '__main__':
  for p in sys.argv[1:]:
    undistort(p)
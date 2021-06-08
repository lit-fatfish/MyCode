import cv2
from skimage.measure import compare_ssim


class Utils:

  def __init__(self):
    pass

  # 比较两帧图片的数据相似度，1为最高 ，img1 = cv2.imread("xxx.jpg")
  def ssim(self, img1, img2):
    # height, width = img1.shape[:2] 
    # print(height, width)
    size = (100, 100)  
    # size = (1080,1920)
    shrink1 = cv2.resize(img1, size, interpolation=cv2.INTER_AREA)  
    shrink2 = cv2.resize(img2, size, interpolation=cv2.INTER_AREA)  
    # print(len(img1),len(shrink1))

    grayA = cv2.cvtColor(shrink1, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(shrink2, cv2.COLOR_BGR2GRAY)


    (score, diff) = compare_ssim(grayA, grayB, full=True)

    return score
  
  def cut_img(self, frame, size):
    # 分为4块
    
    THsize = int(size[0]/2)
    TWsize = int(size[1]/2)

    first_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    first_frame_top_left = first_frame[0:THsize, 0:TWsize]
    first_frame_top_right = first_frame[0:THsize, TWsize:size[1]]
    first_frame_bottom_left = first_frame[THsize:size[0], 0:TWsize]
    first_frame_bottom_right = first_frame[THsize:size[0], TWsize:size[1]]

    # cv2.imwrite("1.jpg",first_frame_top_left)
    # cv2.imwrite("2.jpg",first_frame_top_right)
    # cv2.imwrite("3.jpg",first_frame_bottom_left)
    # cv2.imwrite("4.jpg",first_frame_bottom_right)


    first_frame_top_left = cv2.resize(first_frame_top_left, (50,50))
    first_frame_top_right = cv2.resize(first_frame_top_right, (50,50))
    first_frame_bottom_left = cv2.resize(first_frame_bottom_left, (50,50))
    first_frame_bottom_right = cv2.resize(first_frame_bottom_right, (50,50))


    return first_frame_top_left,first_frame_top_right,first_frame_bottom_left,first_frame_bottom_right
import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils
from PIL import Image
from scipy.spatial.distance import pdist
from skimage.measure import compare_ssim



# 6.计算下面两张图的欧式距离、余弦距离、SSIM、汉明距离、图像指纹、平均值哈希、感知哈希、差异值哈希对比结果

import math



# 欧式距离
def euclidean(image1, image2):
    X = np.vstack([image1, image2])
    return pdist(X, 'euclidean')[0]

# 余弦距离
def cosine(image1, image2):
    X = np.vstack([image1, image2])
    return pdist(X, 'cosine')[0]

# 汉明距离
def hamming(image1, image2):
    """汉明距离"""
    return np.shape(np.nonzero(image1 - image2)[0])[0]

# 图片结构相似度
def ssim(img1, img2):
    # size = (100, 100)  
    # shrink1 = cv2.resize(img1, size, interpolation=cv2.INTER_AREA)  
    # shrink2 = cv2.resize(img2, size, interpolation=cv2.INTER_AREA)  

    # grayA = cv2.cvtColor(shrink1, cv2.COLOR_BGR2GRAY)
    # grayB = cv2.cvtColor(shrink2, cv2.COLOR_BGR2GRAY)


    (score, diff) = compare_ssim(img1, img2, full=True)

    return score

X = [1,2,3,4]
Y = [1,2,3,4]
# print(eucliDist(X,Y))


src_img = cv2.imread("./src_file/5-1.jpg", 0)
dst_img = cv2.imread("./src_file/5-2.jpg", 0)


print(src_img.shape)
print(dst_img.shape)


image1 = np.asarray(src_img).flatten()
image2 = np.asarray(dst_img).flatten()

print("euclidean", euclidean(image1, image2))

print("cosine", cosine(image1, image2))

print("hamming", hamming(image1, image2))

print("ssim", ssim(image1, image2))



cv2.waitKey()
cv2.destroyAllWindows()
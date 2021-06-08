import cv2
import numpy as np


'''
  反复多次，实践-学习-再实践-再学习
  做一个简单的总结：
    导入白板区域，根据
    常规操作，滤波
    找左右的波峰，识别到左右的拐点界限
    根据曲率的阈值=5， 判断为找到稳定第一帧
    将左右波峰内的范围设置为1，其他为0
    map = mask
    arr = 原始图像
'''

# 第一帧std
def first_frame_std(self, rect_img, camera):
  result = {
    "first_frame_map": [], 
    "first_frame_arr": [], 
    "histb": [], 
    "peak_ind": [], 
    "left_stop_index": 0, 
    "right_stop_index": 0
  }
  utils.write_log(str(camera), "first_frame_std: std start !!!!!!")
  # 第一帧像素数量
  first_frame_count = 0
  histb = cv2.calcHist([rect_img], [1], None, [256], [0, 255])
  # 滤波
  histb = utils.arrFilter(histb, 0.9)
  # 找拐点
  all_kness = utils.find_kneed(histb)
  # 寻找波峰
  peak_ind = utils.find_less(histb)
  if not len(peak_ind) and peak_ind[-1] > 125:
    return result
  utils.write_log(str(camera), "first_frame_std: 找波峰波谷 !!!!!!")
  # 寻找左边的波谷
  left_stop_index = 0
  last_fengding = 256 - peak_ind[-1]
  for item in range(100):
    histb_copy = histb.copy()
    if -last_fengding - item - self.std_interval <= -255:
      left_stop_index = 0
    rect_arr = histb_copy[-last_fengding - item - self.std_interval: -last_fengding - item]
    std = np.std(rect_arr, ddof=1)
    if std < self.std_thres:
      left_stop_index = 256 - self.std_interval - item - last_fengding
      break

  # 寻找右边的波谷
  right_stop_index = 0
  for item in range(100):
    histb_copy = histb.copy()
    if -last_fengding + item + self.std_interval >= 0:
      right_stop_index = 255
      break

    rect_arr = histb_copy[-last_fengding + item: - last_fengding + item + self.std_interval]
    std = np.std(rect_arr, ddof=1)

    if std < self.std_thres:
      right_stop_index = 256 + self.std_interval + item - last_fengding
      break

  # print("left_stop_index_arr: ", len(self.left_stop_index_arr), len(self.right_stop_index_arr))
  self.left_stop_index_arr.append(left_stop_index)
  self.right_stop_index_arr.append(right_stop_index)
  if len(self.left_stop_index_arr) > self.std_interval:
    self.left_stop_index_arr = self.left_stop_index_arr[1:]
    self.right_stop_index_arr = self.right_stop_index_arr[1:]

    left_stop_index_std = np.std(self.left_stop_index_arr, ddof=1)
    right_stop_index_std = np.std(self.right_stop_index_arr, ddof=1)
    if left_stop_index_std < self.std_min_thres and right_stop_index_std < self.std_min_thres:
      first_frame_std = True
      utils.write_log(str(camera), "first_frame_std: 找到了稳定的第一帧 !!!!!!")
      # 找到了稳定的第一帧，保存地图
      rect_img = cv2.cvtColor(rect_img, cv2.COLOR_RGB2GRAY)
      rect_img_copy = rect_img.copy()
      first_frame_arr = rect_img.copy()
      for index, item in enumerate(rect_img_copy):
        for itx, its in enumerate(item):
          # print("its: ", its, left_stop_index, right_stop_index)
          if its > left_stop_index and its < right_stop_index:
            rect_img_copy[index][itx] = 1
            first_frame_arr[index][itx] = its
            first_frame_count += 1
          else:
            rect_img_copy[index][itx] = 0
            first_frame_arr[index][itx] = 0
      # 第一帧数据
      first_frame_map = rect_img_copy
      first_frame_darkness = int( np.array(first_frame_arr).sum() / first_frame_count )
      result['first_frame_map'] = first_frame_map
      result['first_frame_arr'] = first_frame_arr
      result['histb'] = histb
      result['peak_ind'] = peak_ind
      result['left_stop_index'] = left_stop_index
      result['right_stop_index'] = right_stop_index
      return result
  return result


### 基准点的查找，可能是第一帧的波峰波谷没有找到，需要采用大津法查找


def update_img_map(self, rect_img, params):
  '''
    这个两个参数是在寻找稳定的第一帧的时候获取的，
    first_frame_map 获取第一帧时，白板上的mask，用于剔除掉本身就是黑色的部分
    first_frame_arr 获取稳定的第一帧时，白板上的那个框
  '''
  first_frame_map = params.get("first_frame_map", None)
  first_frame_arr = params.get("first_frame_arr", None)

  result = {
    "bool": False,
    "first_frame_map": first_frame_map,
    "first_frame_arr": first_frame_arr,
    "first_frame_bool": False
  }

  # 转灰度
  rect_img_gray = cv2.cvtColor(rect_img, cv2.COLOR_RGB2GRAY)
  # 得出白板区域
  rect_img_a = rect_img_gray * first_frame_map # 将本来就是黑色的灰度图筛选掉
  # 类型转换
  rect_img_16 = np.array(rect_img_a, dtype='int16') # 为什么需要类型转换？
  first_frame_arr_16 = np.array(first_frame_arr, dtype='int16')
  # 获取黑度差
  '''第一帧比较白（已经经过mask）减去新的白板区域，那个不够白的，问题：有可能是负的
     第一帧减去最新的白板界面（经过mask筛选），结果=0，说明这两个像素点一样
  '''
  rect_img_dst = first_frame_arr_16 - rect_img_16 
  # 获取不等于0的数组数量
  ''' 获取不等于0的数量，那实际上，肯定会大于的 '''
  now_rect_img_sum = np.sum(rect_img_dst!=0)
  # 求和
  rect_img_copy_sum = rect_img_dst.sum()
  # 每一帧的平均黑度？
  '''平均黑度'''
  if rect_img_copy_sum and now_rect_img_sum:
    rect_img_sum = rect_img_copy_sum / now_rect_img_sum
  else:
    rect_img_sum = 0

  # 组装std 数组
  ''' 24 帧组成一个稳定帧'''
  self.blackness_diff_std_arr.append(rect_img_sum)
  if len(self.blackness_diff_std_arr) > self.blackness_diff_frame_thresh:
    self.blackness_diff_std_arr = self.blackness_diff_std_arr[1:]
  else:
    self.blackness_diff_std_arr.extend([random.randrange(255,1000,5) for item in range(self.blackness_diff_frame_thresh - len(self.blackness_diff_std_arr))])

  # 第一帧黑度是否已经稳定24 fps
  if not self.first_frame_std_bool:
    first_std_result = self.first_std_count(rect_img_sum)
    if first_std_result:
      result['bool'] = True
      return result
    result['first_frame_bool'] = True

  # print("rect_img_sum: ", rect_img_sum)
  # 没有变化 or 变化率超过20
  if rect_img_sum <= self.blackness_diff_thresh or rect_img_sum > 20:
    return result

  # 计算std
  bds_std = np.std(self.blackness_diff_std_arr, ddof=1)
  # print("std: ", bds_std)
  self.std_log.write("std: " + str(bds_std) + '\n')
  # 小于等于std阈值
  if bds_std <= self.blackness_diff_thresh:
    # 大于1跳过
    if self.img_update_index > 1:
      return result
    # 找图片基准点
    res = self.find_frame_std(rect_img.copy())
    res_first_frame_map = res['first_frame_map']
    res_first_frame_arr = res['first_frame_arr']
    # 找到基准点
    if len(res_first_frame_map) and len(res_first_frame_arr):
      # print("T >>>>>>>>>>>>>>>>: ", first_frame_map, first_frame_arr)
      self.img_update_index += 1
      result['bool'] = True
      result['first_frame_arr'] = res_first_frame_arr
      result['first_frame_map'] = res_first_frame_map
      self.temp_left_stop_index_arr = []
      self.temp_right_stop_index_arr = []
      return result
    return result
  self.img_update_index = 0
  return result


def first_std_count(self, rect_img_sum):
  self.first_diff_std_arr.append(rect_img_sum)
  if len(self.first_diff_std_arr) > self.first_diff_std_arr_thresh:
    self.first_diff_std_arr = self.first_diff_std_arr[1:]
  else:
    return
  # 计算std
  fds_std = np.std(self.first_diff_std_arr, ddof=1)
  if fds_std < self.first_diff_std_thresh:
    self.first_frame_std_bool = True
    return True
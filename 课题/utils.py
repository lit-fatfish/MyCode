import cv2
import numpy as np


class Utils():
  def __init__(self):
    pass


  '''
    frame:图片源
    axis_x_arr: y轴数据
    axis_origin：0点坐标
    axis_size： 坐标系大小
    y_max： y轴最大值
  '''
  def draw_axis(self, frame, axis_x_arr, axis_origin=[], axis_size=[], y_max=0):
    axis_fill_color = (255, 255, 255)           # 柱状图颜色
    axis_color = (255, 0, 0)
    axis_font = cv2.FONT_HERSHEY_SIMPLEX        # 定义字体
    axis_y_font_size = .4                       # y轴字体大小
    axis_y_font_color = (0,0,255)               # y轴字体大小
    axis_y_font_weight = 1                      # y轴字体大小
    axis_y_num = 5                              # y轴刻度数量
    screen_h, screen_w = frame.shape[:2]

    # print(axis_x_arr)
    # 数据类型检查
    # print("axis_x_arr: ", axis_x_arr)
    # if not isinstance(axis_x_arr, list):
    #   return frame
    # print(len(axis_x_arr))
    # print("ok")
    # 坐标系0点
    axis_origin_x = axis_origin[0] if len(axis_origin) > 0 else 50
    axis_origin_y = axis_origin[1] if len(axis_origin) > 0 else screen_h - 50
    # 坐标系大小
    axis_size_w = axis_size[0] if len(axis_size) > 0 else int(screen_w/4)
    axis_size_h = axis_size[1] if len(axis_size) > 0 else int(screen_h/4)
    # x轴和y轴步长
    axis_x_step_distance = axis_size_w / len(axis_x_arr)  # 计算直方图后是256
    axis_y_step_distance = axis_size_h / axis_y_num
    # y轴最大高度
    y_max = y_max if y_max > 0 else max(axis_x_arr)
    # y轴高度步长
    axis_y_h_step = axis_size_h / axis_y_num
    # y轴值步长
    axis_y_step = y_max/axis_y_num if y_max > 0 else 1 if max(axis_x_arr) <= 0 else max(axis_x_arr)[0]/axis_y_num

    # 画x和y轴
    # 帧  (起点线坐标) （结束线坐标） 颜色
    frame = cv2.line(frame, (axis_origin_x, axis_origin_y), (axis_origin_x + axis_size_w, axis_origin_y), axis_color)
    frame = cv2.line(frame, (axis_origin_x, axis_origin_y), (axis_origin_x, axis_origin_y - axis_size_h), axis_color)

    # 画y轴刻度和值
    for item in range(axis_y_num+1):
      start_point = (int(axis_origin_x), int(axis_origin_y - item * axis_y_step_distance))
      end_point = (int(axis_origin_x - 10), int(axis_origin_y - item * axis_y_step_distance))
      frame = cv2.line(frame, start_point, end_point, axis_color)
      try:
        # print("axis_y_step: ", axis_y_step)
        frame = cv2.putText(frame, str(int(round(axis_y_step*item, 2))), ( int(end_point[0] - 30), int(end_point[1]) ), axis_font, axis_y_font_size, axis_y_font_color, axis_y_font_weight)
      except:
        print("axis_y_step: ", axis_y_step, item, end_point, max(axis_x_arr), axis_y_num, max(axis_x_arr)/axis_y_num)

    # 画x轴数据
    for index, item_x in enumerate(axis_x_arr):
      # y_distance = 0 if item_x in [0, 0.0] else ( item_x/math.ceil(max(axis_x_arr)) ) * axis_size_h
      y_distance = 0 if max(axis_x_arr) <= 0 else item_x/max(axis_x_arr) * axis_size_h
      fill_point = [
        (axis_origin_x + axis_x_step_distance*index, axis_origin_y),
        (axis_origin_x + axis_x_step_distance*index + axis_x_step_distance, axis_origin_y),
        (axis_origin_x + axis_x_step_distance*index + axis_x_step_distance, axis_origin_y - y_distance),
        (axis_origin_x + axis_x_step_distance*index, axis_origin_y - y_distance),
      ]
      cv2.fillPoly(frame, [np.array(fill_point, dtype=np.int)], axis_fill_color)
    return frame


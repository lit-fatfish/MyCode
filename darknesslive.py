import os, json, time, queue, cv2, threading
import subprocess as sp
import numpy as np
from extend.utils import Utils
from extend.dn_video import Detection
import extend.darknet as cnet
from extend.variables import Variables

dn = Detection()            # 推理程序
utils = Utils()             # 初始化工具函数

var = Variables()           # 初始化变量

class Live(object):
  def __init__(self, rtmpUrl, camera_path, model_config):
    self.frame_queue = queue.Queue(maxsize=10)
    self.command = ""
    self.size = (1280, 720)
    self.fps = 25
    # 自行设置
    self.rtmpUrl = rtmpUrl
    self.camera_path = camera_path
    self.axis_font = cv2.FONT_HERSHEY_SIMPLEX         # 定义字体
    self.axis_y_font_size = .8                        # y轴字体大小
    self.axis_y_font_color = (255,0,0)                # y轴字体大小
    self.axis_y_font_weight = 3                       # y轴字体大小
    self.model_config = model_config                  # 模型配置

    self.skip_frame_index = 20                        # 跳帧
    self.rect_img_thres = 0.2                         # 检出框缩小倍数
    self.binarization_thres = 0.5                     # 二值化阈值
    self.now_blackness = 0                            # 当前黑度百分比


    self.filedata = {
      "xmin": 0,
      "ymin": 0,
      "xmax": 0,
      "ymax": 0
    }

    self.color = (255, 0, 0)                          # 


  def read_frame(self):
    print("开启推流")
    cap = cv2.VideoCapture(self.camera_path)

    # Get video information
    self.fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    self.size = (width, height)

    # ffmpeg command
    self.command = ['ffmpeg',
      '-y',
      '-f', 'rawvideo',
      '-vcodec','rawvideo',
      '-pix_fmt', 'bgr24',
      '-s', "{}x{}".format(width, height),
      '-r', str(self.fps),
      '-i', '-',
      '-c:v', 'libx264',
      '-an',
      '-pix_fmt', 'yuv420p',
      '-b:v', '2000k',
      '-preset', 'ultrafast',
      '-f', 'rtsp', 
      self.rtmpUrl]

    # read webcamera
    while(cap.isOpened()):
      ret, frame = cap.read()
      if not ret:
        print("Opening camera is failed")
        time.sleep(1)
        cap.open(self.camera_path)
        continue
      # put frame into queue
      self.frame_queue.put(frame)

  def push_frame(self):
    # 防止多线程时 command 未被设置
    while True:
      if len(self.command) > 0:
        # 管道配置
        p = sp.Popen(self.command, stdin=sp.PIPE)
        break

    
    frame_index = 0
    # 多久检测一次白板
    board_frame_thres = 25

    darknet_image = cnet.make_image(self.size[0], self.size[1], 3)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    videoWriter = cv2.VideoWriter("test_video.mp4", fourcc, 24, (1920, 1080))
    num = 0
    while True:
      if self.frame_queue.empty() != True:
        frame = self.frame_queue.get()
        
        if len(frame) == 0:
          continue

        # 帧数自增
        frame_index += 1

        # 检测白板
        if frame_index % board_frame_thres == 0:

          # 推理
          board_params = {
            "frame": frame,
            "model_conf": self.model_config,
            "darknet_image": darknet_image,
            "size": self.size,
            "thresh": 0.8
          }
          ring_detections = dn.detection_video(board_params)

          # 获取白板坐标
          board_arr = dn.res_type_point(ring_detections, 'board')
          # print("board_arr: ", board_arr)
          if len(board_arr) > 0:
            self.filedata = board_arr[0]
          else:
            self.filedata = {
              "xmin": 0,
              "ymin": 0,
              "xmax": 0,
              "ymax": 0
            }

        # 跳帧
        if frame_index % self.skip_frame_index != 0:
          continue

        if self.filedata['xmin'] == 0 and self.filedata['xmax'] == 0 and \
            self.filedata['ymin'] == 0 and self.filedata['ymax'] == 0:
          print("没有找到白板")
          continue

        rect_pt1 = (self.filedata['xmin'], self.filedata['ymin'])
        rect_pt2 = (self.filedata['xmax'], self.filedata['ymax'])

        cv2.rectangle(frame, rect_pt1, rect_pt2, (0, 0, 255), 2)

        diff_x = int( (self.filedata['xmax'] - self.filedata['xmin']) * self.rect_img_thres )
        diff_y = int( (self.filedata['ymax'] - self.filedata['ymin']) * self.rect_img_thres )

        pt1 = (self.filedata['xmin'] + diff_x, self.filedata['ymin'] + diff_y)
        pt2 = (self.filedata['xmax'] - diff_x, self.filedata['ymax'] - diff_y)

        # 截出需要检测的面积
        rect_img = frame[pt1[1]:pt2[1], pt1[0]:pt2[0]].copy()
        # 直方图
        histb = cv2.calcHist([rect_img], [1], None, [256], [0, 255])
        # 滤波
        histb = utils.arrFilter(histb, 0.9)
        # 画蓝色框
        cv2.rectangle(frame, pt1, pt2, self.color, 2)
        # 转为灰度图
        rect_img = cv2.cvtColor(rect_img, cv2.COLOR_BGR2GRAY)
        # 画直方图
        frame = utils.draw_axis(frame, histb, (40, 900), [], int(max(histb)))
        # 二值化
        rect_img[rect_img > 255*self.binarization_thres] = 255
        rect_img[rect_img <= 255*self.binarization_thres] = 0

        rect_img_h, rect_img_w = rect_img.shape
        self.now_blackness = np.sum(rect_img == 0) / (rect_img_h * rect_img_w)

        # 显示黑度
        frame = cv2.putText(frame, 'darkness: ' + str(self.now_blackness), (20, 150), self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
        # 添加二值化图
        temp_rect_img = cv2.cvtColor(rect_img, cv2.COLOR_GRAY2BGR)
        fillPointYmin, fillPointYmax = self.size[1] - rect_img_h - 60, self.size[1] - 60
        fillPointXmin, fillPointXmax = self.size[0] - rect_img_w - 30, self.size[0] - 30
        frame[fillPointYmin:fillPointYmax, fillPointXmin:fillPointXmax] = temp_rect_img

        print(len(frame))
        # write to pipe
        p.stdin.write(frame.tostring())
        num += 1
        print(num)
        if num > 50 and num < 100:
          videoWriter.release()
          num = 120
        elif num < 50:
          videoWriter.write(frame)

          



  # 运行
  def run(self):
    threads = [
      threading.Thread(target=Live.read_frame, args=(self,)),
      threading.Thread(target=Live.push_frame, args=(self,))
    ]
    [thread.setDaemon(True) for thread in threads]
    [thread.start() for thread in threads]
    return threads



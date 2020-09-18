import os, json, time, queue, cv2, threading
import subprocess as sp
import numpy as np
from extend.utils import Utils
from extend.dn_video import Detection
from extend.service import Service
import extend.darknet as cnet
from extend.rabbitMQ import Rabbit
from extend.variables import Variables

service = Service()         # 初始化服务函数
dn = Detection()            # 推理程序
utils = Utils()             # 初始化工具函数

var = Variables()           # 初始化变量

class Live(object):
  def __init__(self, rtmpUrl, camera_path, model_config, camera):
    self.frame_queue = queue.Queue(maxsize=10)
    self.camera = camera
    self.darkness_level = utils.load_yaml(var.config_path['darkness_level'])
    self.command = ""
    self.size = (1280, 720)
    self.fps = 25
    # 自行设置
    self.rtmpUrl = rtmpUrl
    self.camera_path = camera_path
    self.axis_font = cv2.FONT_HERSHEY_SIMPLEX         # 定义字体
    self.axis_y_font_size = .8                        # y轴字体大小
    self.axis_y_font_color = (0,0,255)                # y轴字体大小
    self.axis_y_font_weight = 3                       # y轴字体大小
    self.model_config = model_config                  # 模型配置
    self.peak_ind = 0

    self.skip_frame_index = 20                        # 跳帧
    self.darkness_skip_index = 2                      # 跳帧
    self.max_rect_img_sum = 0                         # 最大黑度
    self.rect_img_thres = 0.2                         # 检出框缩小倍数
    self.binarization_thres = 0.5                     # 二值化阈值
    self.now_blackness = 0                            # 当前黑度百分比
    self.black_detection = 0                          # 是否开始检测 0 校准模式 1 检测模式
    self.source_path = 0                              # 源视频流
    self.dist_path = 0                                # 推理视频流
    self.source_output = 0                            # 源视频路径
    self.dist_output = 0                              # 推理视频路径
    # 返回数据
    self.result_data = {
      "source_name": "",                              # 源视频名
      "detection_name": "",                           # 推理视频名
      "evidence_img": [],                                 # 图片列表
      "level": 0,                                     # 当前黑度等级
      "board_bool": 0                                 # 是否有白板
    }
    self.photo_num_thres = 4                          # 拍照数量阈值
    self.now_photo_num = 0                            # 当前拍照数量
    self.level_arr = []

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

    skip_frame_index = 2
    frame_index = 0
    # 多久检测一次白板
    board_frame_thres = 25

    darknet_image = cnet.make_image(self.size[0], self.size[1], 3)

    while True:
      if self.frame_queue.empty() != True:
        frame = self.frame_queue.get()

        if len(frame) == 0:
          continue

        # 帧数自增
        frame_index += 1

        # 检测白板
        if frame_index % board_frame_thres == 0:
          # 拍4张照片
          
          if self.photo_num_thres > self.now_photo_num and self.black_detection:
            self.now_photo_num += 1
            jpg_filename = str(time.time()) + '.jpg'
            jpg_path = os.path.join(var.local_path['keyframe_path'], jpg_filename)
            cv2.imwrite(jpg_path, frame)
            self.result_data['evidence_img'].append(jpg_filename)

          # 推理
          board_params = {
            "frame": frame,
            "model_conf": self.model_config,
            "darknet_image": darknet_image,
            "size": self.size,
            "thresh": 0.8
          }
          # print("self.model_config: ", self.model_config)
          ring_detections = dn.detection_video(board_params)

          # 获取白板坐标
          board_arr = dn.res_type_point(ring_detections, 'board')
          # print("board_arr: ", board_arr)
          if len(board_arr) > 0:
            self.filedata = board_arr[0]
            # 设置白板存在
            self.result_data['board_bool'] = 1
          else:
            self.filedata = {
              "xmin": 0,
              "ymin": 0,
              "xmax": 0,
              "ymax": 0
            }

        if frame_index % skip_frame_index != 0:
          continue

        # 写入视频
        if self.black_detection != 0:
          self.source_output.write(frame)

        if self.filedata['xmin'] == 0 and self.filedata['xmax'] == 0 and \
            self.filedata['ymin'] == 0 and self.filedata['ymax'] == 0:
          p.stdin.write(frame.tostring())
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
        # 计算黑度等级
        darkness = service.darkness_sqrt(self.now_blackness, self.darkness_level['camera'][self.camera])
        # 显示黑度
        frame = cv2.putText(frame, 'darkness: ' + str(self.now_blackness), (20, 150), self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
        # 显示林格曼黑度
        frame = cv2.putText(frame, 'darkness level: ' + str(darkness), (20, 120), self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
        # 添加二值化图
        temp_rect_img = cv2.cvtColor(rect_img, cv2.COLOR_GRAY2BGR)
        fillPointYmin, fillPointYmax = self.size[1] - rect_img_h - 60, self.size[1] - 60
        fillPointXmin, fillPointXmax = self.size[0] - rect_img_w - 30, self.size[0] - 30
        frame[fillPointYmin:fillPointYmax, fillPointXmin:fillPointXmax] = temp_rect_img
        # 写入视频
        if self.black_detection != 0:
          self.level_arr.append(darkness)
          # 黑度值
          if len(self.level_arr) > 45:
            frame = cv2.putText(frame, 'G: ' + str(self.level_arr[:45]), (5, 180), self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
            frame = cv2.putText(frame, 'G: ' + str(self.level_arr[45:]), (5, 210), self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
          else:
            frame = cv2.putText(frame, 'G: ' + str(self.level_arr), (5, 180), self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
          self.dist_output.write(frame)
        # write to pipe
        p.stdin.write(frame.tostring())

  # 重置 darkness_level.yaml 文件
  def reset_darkness_level(self):
    # 遍历摄像头列表
    for item in self.darkness_level['camera']:
      darkness_level['camera'][item] = {
        0: 0,
        1: 20,
        2: 40,
        3: 60,
        4: 80,
        5: 100
      }
    utils.write_yaml(var.config_path['darkness_level'], darkness_level)

  # 更新黑度等级
  def update_darkness_level(self, result):
    camera = str(result['camera'])
    level = int(result['level'])
    # darkness_level = utils.load_yaml(var.config_path['darkness_level'])
    print("camera: ", camera, level, self.darkness_level, self.now_blackness)
    self.darkness_level['camera'][camera][level] = int( self.now_blackness * 100 )
    print("darkness_level: ", self.darkness_level)
    utils.write_yaml(var.config_path['darkness_level'], self.darkness_level)

  # 获取rabbitMQ消息处理
  def consumer_controll(self, ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    result = json.loads( body.decode() )
    print("consumer_controll: ", result, type(result))
    if result['type'] == 'update':
      self.update_darkness_level(result)
    elif result['type'] == 'reset':
      self.reset_darkness_level()

  # 重置数据
  def reset_data(self):
    self.result_data = {
      "source_name": "",                              # 源视频名
      "detection_name": "",                           # 推理视频名
      "evidence_img": [],                                 # 图片列表
      "level": 0,                                     # 当前黑度等级
      "board_bool": 0                                 # 是否有白板
    }
    # 停止录制视频
    self.black_detection = 0
    self.source_output = 0
    self.dist_output = 0

    # 重置输出路径
    self.source_output = 0
    self.dist_output = 0
    self.source_path = 0
    self.dist_path = 0
    self.now_photo_num = 0
    

  # 发送检测结果
  def send_result(self):
    rabbit = Rabbit()           # rabbitMQ
    print("self.level_arr: ", self.level_arr)
    self.result_data['level'] = int(np.mean(self.level_arr)) if len(self.level_arr) else 0
    rabbit.create_queue(var.rabbitmq_queue['result_black'], self.result_data)
    self.level_arr = []

  # 黑度测试
  def blacktest(self, ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    result = json.loads( body.decode() )
    print("blacktest: ", result, type(result))
    if result['type'] == 'start':
      # 如果有正在进行的任务，则不处理
      if self.source_path != 0 or self.dist_path != 0:
        return

      self.source_path = os.path.join(var.local_path['nginx_path'], result['source_name'])
      self.dist_path = os.path.join(var.local_path['dist_path'], result['dist_name'])
      # 填充
      self.result_data['source_name'] = result['source_name']
      self.result_data['detection_name'] = result['dist_name']
      # 创建 VideoWriter对象
      codec = cv2.VideoWriter_fourcc(*'XVID')
      self.source_output = cv2.VideoWriter(self.source_path, codec, self.fps, self.size)
      self.dist_output = cv2.VideoWriter(self.dist_path + '.mp4', codec, self.fps, self.size)
      # 开始录制视频
      self.black_detection = 1
    elif result['type'] == 'stop':
      # 如果没有正在进行的任务，则不处理
      if self.source_path == 0 or self.dist_path == 0:
        return

      dist_path = self.dist_path[:]

      self.send_result()
      self.reset_data()
      # print("dist_path: ", dist_path)
      os.popen("ffmpeg -i {} -c:v libx264 -c:a copy {} && rm -rf {}".format(dist_path + '.mp4', dist_path, dist_path + '.mp4'))
      # os.remove(dist_path + '.mp4')


  # 监听黑度校准请求
  def listen_darkness(self):
    rabbit = Rabbit()           # rabbitMQ
    rabbit.consumer(var.rabbitmq_queue['darkness_level'] + '_' + str(self.camera), self.consumer_controll)

  # 黑度检测
  def listen_blacktest(self):
    rabbit = Rabbit()           # rabbitMQ
    rabbit.consumer(var.rabbitmq_queue['blacktest'] + '_' + str(self.camera), self.blacktest)

  # 运行
  def run(self):
    threads = [
      threading.Thread(target=Live.read_frame, args=(self,)),
      threading.Thread(target=Live.push_frame, args=(self,)),
    ]
    [thread.setDaemon(True) for thread in threads]
    [thread.start() for thread in threads]
    return threads



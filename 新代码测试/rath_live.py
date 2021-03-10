import os, json, time, queue, threading, cv2, pickle,struct,socket
from threading import Timer
from skimage.measure import compare_ssim
import subprocess as sp
import numpy as np
from extend.service import Service
import extend.darknet as cnet
from extend.utils import Utils
from extend.dn_video import Detection
from extend.rabbitMQ import Rabbit
from extend.variables import Variables
from package.dn import Dn 
from extend.redis_tools import RedisTools
from package.m import Merge
from package.cvdraw import CvDraw




service = Service()         # 业务逻辑程序
dn = Detection()            # 推理程序
utils = Utils()             # 初始化工具函数
var = Variables()           # 初始化变量
draw = CvDraw()             # 绘图工具


r = RedisTools("172.17.0.1", 6379, "anlly12345", 0)
m = Merge()                 # 初始化观测工具

port = 8003


class Live(object):
  def __init__(self, args_data):
    self.frame_queue = queue.Queue(maxsize=2)
    self.command = ""
    self.size = (0, 0)
    self.fps = 25
    # 自行设置
    self.rtmpUrl = args_data['rtmpUrl'] + "_video"
    self.camera_path = args_data['camera_rtsp']
    self.ring_data = args_data['board_model_data']
    self.camera = args_data['camera']
    self.is_board = args_data['is_board']
    self.serial = args_data['serial']
    self.axis_font = cv2.FONT_HERSHEY_SIMPLEX         # 定义字体
    self.axis_y_font_size = .8                        # y轴字体大小
    self.axis_y_font_color = (255,0,0)                # y轴字体大小
    self.axis_y_font_weight = 3                       # y轴字体大小
    self.dn_darkness_bool = True                      # 是否开始检测黑烟

    self.skip_frame_index = 2                         # 跳帧
    self.darkness_skip_index = 2                      # 跳帧
    self.max_rect_img_sum = 0                         # 最大黑度
    self.filedata = {
      "xmin": 0,
      "ymin": 0,
      "xmax": 0,
      "ymax": 0
    }

    self.color = (255, 0, 0)                          # 

    # 第一帧是否稳定， True 稳定
    self.first_frame_std = False

    # 帧数
    self.frame_index = 0
    self.diff_black_arr = []
    self.histb = 0
    self.peak_ind = []
    self.left_stop_index = 0
    self.right_stop_index = 0
    # 是否相交
    self.is_mater = False
    # 当前帧数
    self.now_index = 0
    

    self.result_dn_data = {
      "source_name": "",                              # 源视频名
      "detection_name": "",                           # 推理视频名
      "evidence_img": [],                             # 图片列表
      "level": 0,                                     # 当前黑度等级
      "board_bool": 0,                                # 是否有白板
      "is_board":self.is_board,                       # 找板程序是否有白板
      "result":0,                                     # 是否有黑烟
      "serial": self.serial,
      # "smoke_change":0,  
      "dot_id": str(self.camera)                           # 网点id
                
    }
    self.max_darkness_frame = []                      # 最大黑度帧数据

    source_name =  str(time.time()) + '_source.mp4'
    dist_name = str(time.time()) + '_detection.mp4'
    self.source_path = os.path.join(var.local_path['nginx_path'], source_name)
    self.dist_path = os.path.join(var.local_path['dist_path'], dist_name)
    # 填充
    self.result_dn_data['source_name'] = source_name
    self.result_dn_data['detection_name'] = dist_name
    

    # 时间管理变量
    self.time_overtime = 0 # 设置服务器超时时间，大于10s时退出程序
    self.time_overtime_of_rath = 0 # 测烟时间超时，大于10分钟就自动退出。
    self.timer_manager(1)

    # redis数据处理 

    self.start_time = time.time()
    self.data = r.get_values(self.camera)
    self.data['rath_start'] =time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    self.data['status'] = "in rath ..."
    r.set_values(self.camera ,self.data)

    # 异物检查参数
    self.first_3,self.first_4,self.first_5,self.first_6 = ([] for i in range(4))
    self.threshold_ssim = 0.84
    self.pass_frame_num = 0  # 图像对比超过默认分数时，记录

    # 检查摄像头是否启动
    if not utils.check_camera(self.camera_path):
      print("camera error")
      utils.write_log(str(self.camera), "__init__ 摄像头异常")
      self.send_dn_result()
    
    # 推理数据
    self.ring_detections = []
    self.board_arr = []
    
    # 初始化推理socket
    params = {
      "ip": "0.0.0.0",
      "port": port,
      "dot_id": self.camera    

    }
    self.dn_live = Dn(params)
    self.dn_live.run()

    # 模型
    self.model_id = utils.model_id_convert("board")
    self.model_id_byte = utils.meal_byte(self.model_id, self.dn_live.model_len)

    # 黑度板
    self.rect_img_thres = 0.3                         # 检出框缩小倍数
    self.binarization_thres = 0.5                     # 二值化阈值
    self.darkness_level = utils.load_yaml(var.config_path['darkness_level'])
    self.lingerman_darkness = 0        
    self.is_rb_board = 0                              # 判断是林格曼板还是白板，0不是，1是
    self.lingerman_bool = 0                           # 判断是林格曼板时为1，不再进行霍夫检测
    self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    self.client.connect(('172.17.0.1', 7003))

    # 结束命令
    self.kill_command = "ps -ef | grep -v grep | grep rath.py | grep " + self.camera_path + "   | awk '{print $2}' | xargs kill"
    print(self.kill_command)
    

  def line_detection(self, rect_img):
    # 边缘检测 + 霍夫变换
    edges = cv2.Canny(rect_img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 118)
    minLineLength = 30 # height/32
    maxLineGap = 10 # height/40

    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50, minLineLength, maxLineGap)
    return lines

  # 定时管理函数
  def timer_manager(self,timing):
    # 每秒进入此函数一次
    self.time_overtime += 1
    self.time_overtime_of_rath += 1

    print("self.time_overtime", self.time_overtime)

    if self.time_overtime >= 10:
      # 服务端10s无反应，退出程序
      # self.send_dn_result()
      print("Server timeout, exit program")
      utils.write_log(str(self.camera), "timer_manager 推理服务端10s无反应，退出程序")
      self.dn_darkness_bool = False
      # 2020年12月24日 14:24:07 新增测试 推理超时，保证正常的数据结果返回
      r8 = RedisTools("172.17.0.1", 6379, "anlly12345", 8)
      r8.write_queue("reasoningEndList", str(self.serial))
      time.sleep(2)

      self.send_dn_result()
      os.system(self.kill_command)
      exit(0)
    # 测烟时间最大为10分钟
    if self.time_overtime_of_rath >= 600:
      # self.send_dn_result()
      # 处理找板视频和测烟视频
      r8 = RedisTools("172.17.0.1", 6379, "anlly12345", 8)
      r8.write_queue("reasoningEndList", str(self.serial))
      time.sleep(2)
      
      utils.write_log(str(self.camera), "timer_manager 测烟时间最大为10分钟，退出程序")
      self.dn_darkness_bool = False
      # exit(0)
    if self.dn_darkness_bool:
      t = Timer(timing, self.timer_manager, (timing,))
      t.start()

  def read_detection(self):
    recv_data = b''
    payload_size = struct.calcsize(">L")
    last_count=0
    startTime=0
    while True:
      time.sleep(0.035)
      if self.result_dn_data['board_bool'] != 1:
        detections, recv_data = self.dn_live.get_detection(recv_data, self.size)
        self.ring_detections = detections
        print("self.ring_detections", self.ring_detections)

      last_count += 1
      if last_count % 100 == 0:
        endTime = int(time.time() * 1000)
        diffTime = endTime - startTime
        if diffTime == 0:
          diffTime = 1
        print("recv fps: ", round(1000 * 100/diffTime,2))
        startTime = int(time.time() * 1000)

  def read_frame(self):
    print("开启推流")
    cap = cv2.VideoCapture(self.camera_path)

    # Get video information
    self.fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    self.size = (width, height)

    # read webcamera
    while(cap.isOpened()):
      ret, frame = cap.read()
      # ret, frame = cap.read()
      if not ret:
        print("Opening camera is failed")
        utils.write_log(str(self.camera), "read_frame 摄像头打开失败")
        time.sleep(1)
        cap.open(self.camera_path)
        continue
      # put frame into queue
      self.frame_queue.queue.clear()
      self.frame_queue.put(frame)

  def push_frame(self):
    # 等待 size 初始化完成
    while True:
      time.sleep(0.5)
      if self.size[0] != 0 and self.size[1] != 0:
        break
      continue

    # 创建 VideoWriter对象
    codec = cv2.VideoWriter_fourcc(*'XVID')
    self.source_output = cv2.VideoWriter(self.source_path + '.mp4', codec, self.fps, self.size)
    self.dist_output = cv2.VideoWriter(self.dist_path + '.mp4', codec, self.fps, self.size)

    # 读取安全帽
    # darknet_image = cnet.make_image(self.size[0], self.size[1], 3)
    rect_img = []

    # 第一帧的源数据
    self.first_frame = []
    self.t_board_arr = [] # 放大后的框数据

    # blackness diff std arr
    blackness_first_std = False
    # 黑度list
    blackness_list = []
    # 总数 100
    blackness_list_count = 100
    update_count = 0

    utils.write_log(str(self.camera), "push_frame 初始化完成，进入while")
    while True:
      if self.frame_queue.empty() != True:
        frame = self.frame_queue.get()
        pure_frame = frame.copy()
        
        # 清除超时标志
        self.time_overtime = 0

        # 没有帧数据
        if len(frame) == 0:
          continue
        
        # 停止检测时
        if not self.dn_darkness_bool:
          utils.write_log(str(self.camera), "push_frame 停止检测中...")
          # 发送识别结果
          self.send_dn_result()
          self.source_output.release()
          self.dist_output.release()

          utils.write_log(str(self.camera), "push_frame 推理视频写入转码队列")
          # 推理视频同样写入redis中，等待转码
          r.write_queue("dst_video_list", os.path.join(var.local_path['dist_path'], self.dist_path + '.mp4'))

          # 源视频写入redis中，等待转码
          r.write_queue("source_video_list", os.path.join(var.local_path['nginx_path'], self.source_path + '.mp4'))

          utils.write_log(str(self.camera), "push_frame 源视频写入转码队列")
          utils.write_log(str(self.camera), "----------------测烟结束---------------")
          os.system(self.kill_command)
          exit(0)

        # 写入源视频
        self.source_output.write(frame)
    
        self.now_index += 1
        if not self.first_frame_std and self.now_index % self.skip_frame_index == 0:
          # 没找到板，推理
          if self.result_dn_data['board_bool'] != 1:
            if self.max_darkness_frame == []:
              self.max_darkness_frame = pure_frame
            self.dn_live.send_frame(frame, self.model_id_byte)
            if not self.ring_detections:
              print("pass...")
              # 写入推理视频
              self.dist_output.write(frame)
              continue

            # 获取白板坐标
            self.board_arr = dn.res_type_point(self.ring_detections, 'board')
            self.rb_board_arr = dn.res_type_point(self.ring_detections, 'RB_board')

            if self.filedata['xmin'] == 0 and self.filedata['ymin'] == 0 and \
              self.filedata['xmax'] == 0 and self.filedata['ymax'] == 0:
              
              if len(self.rb_board_arr) > 0:
                self.is_rb_board = 1
                self.filedata = utils.find_board_center(self.rb_board_arr, self.size)
              elif len(self.board_arr) > 0:
                self.is_rb_board = 0
                self.filedata = utils.find_board_center(self.board_arr, self.size)
              else:
                self.filedata = {
                  "xmin": 0,
                  "ymin": 0,
                  "xmax": 0,
                  "ymax": 0
                }

              utils.write_log(str(self.camera), "push_frame 获取白板坐标:")
              utils.write_log(str(self.camera), self.filedata)

              # 写redis
              self.data = r.get_values(self.camera)
              self.data['filedata'] = self.filedata
              r.set_values(self.camera ,self.data)

              # utils.write_log(str(self.camera), "push_frame 写入观测redis:")
              # utils.write_log(str(self.camera), self.data)
              # 如果没有找到白板
            if self.filedata['xmin'] == 0 and self.filedata['ymin'] == 0 and\
                self.filedata['xmax'] == 0 and self.filedata['ymax'] == 0:
              self.dist_output.write(frame)
              continue

        # 截取白板区域
        pt1 = (self.filedata['xmin'], self.filedata['ymin'])
        pt2 = (self.filedata['xmax'], self.filedata['ymax'])
        rect_img = frame[pt1[1]:pt2[1], pt1[0]:pt2[0]]

        # 临时添加测试
        if self.max_rect_img_sum:
          blackness = utils.darkness_level(self.max_rect_img_sum)
          frame = cv2.putText(frame, 'max darkness: ' + str(self.max_rect_img_sum), (20, 300),self.axis_font, self.axis_y_font_size, (0,0,255), self.axis_y_font_weight)
          frame = cv2.putText(frame, 'blackness: ' + str(blackness), (20, 320), self.axis_font,self.axis_y_font_size, (0,0,255), self.axis_y_font_weight)
          draw.add_txt(frame, {
            "content": "base img update count: " + str(update_count),
            "point": (20, 360)
          })

        # 获取计算黑度所需的条件
        if not self.first_frame_std and len(rect_img):
          try:
            result = service.first_frame_std(rect_img, self.camera)
            first_frame_map = result['first_frame_map']
            first_frame_arr = result['first_frame_arr']
            self.histb = result['histb']
            self.peak_ind = result['peak_ind'] 
            self.left_stop_index = result['left_stop_index'] 
            self.right_stop_index = result['right_stop_index']

            if len(first_frame_map) != 0 and len(first_frame_arr) != 0:
              self.first_frame_std = True
              self.result_dn_data['board_bool'] = 1
              self.darkness_skip_index = 1
              utils.write_log(str(self.camera), "push_frame 已经找到第一帧的画面")
              print(">>>>>>>>>>>>>>>>>>>> first std success!")
            frame = cv2.putText(frame, "not found board", (20,200), cv2.FONT_HERSHEY_SIMPLEX, 1,[255, 255, 255],2)
            self.dist_output.write(frame)
            continue
          except Exception as e:
            print(e)
            utils.write_log(str(self.camera), "错误" + str(e))
          
        # 更新基准点
        if self.first_frame_std:
          # 画框
          if len(self.filedata):
            frame = cv2.rectangle(frame, (self.filedata['xmin'], self.filedata['ymin']), (self.filedata['xmax'], self.filedata['ymax']), (0,0,255), 2)
            frame = dn.drawScaleBox(frame, self.filedata, self.size)  # 画扩大的框

          params = {
            "first_frame_map": first_frame_map,
            "first_frame_arr": first_frame_arr
          }
          # 更新基准点
          update_img_std = service.update_img_map(rect_img, params)
          map_h, map_w, _ = update_img_std['first_frame_map'].shape
          map_sum = np.sum(update_img_std['first_frame_map']!= 0) / (map_h * map_w)
          if update_img_std['bool'] and map_sum > 0.3:
            first_frame_arr = update_img_std['first_frame_arr']
            first_frame_map = update_img_std['first_frame_map']
            blackness_first_std = True
            update_count += 1
          if update_img_std['first_frame_bool']:
            self.dist_output.write(frame)

        if blackness_first_std and self.first_frame_std and self.now_index % self.darkness_skip_index == 0:
          # 找到白板
          self.result_dn_data['board_bool'] = 1

          self.frame_index += 1
         
          ## 判断是否是林格曼板
          diff_x = int( (self.filedata['xmax'] - self.filedata['xmin']) * self.rect_img_thres )
          diff_y = int( (self.filedata['ymax'] - self.filedata['ymin']) * self.rect_img_thres )

          lingerman_pt1 = (self.filedata['xmin'] + diff_x, self.filedata['ymin'] + diff_y)
          lingerman_pt2 = (self.filedata['xmax'] - diff_x, self.filedata['ymax'] - diff_y)
          # 截出需要检测的面积
          lingerman_rect_img = frame[lingerman_pt1[1]:lingerman_pt2[1], lingerman_pt1[0]:lingerman_pt2[0]].copy()
          if self.frame_index <= 5 and self.lingerman_bool != 1:
            print("检测是否是林格曼板")
            line = self.line_detection(lingerman_rect_img)
            print("is_rb_board", self.is_rb_board)
            print("line", line)
            utils.write_log(str(self.camera), "push_frame 检测是否是林格曼板")
            if line is not None and self.is_rb_board == 1:
              utils.write_log(str(self.camera), "push_frame 检测到线，并且是林格曼板")
              self.lingerman_bool = 1
              print("self.lingerman_bool", self.lingerman_bool)
              scalePix = 10
              print("放大")
              m.move_3d_enlarge(self.filedata, self.client, scalePix, self.result_dn_data, self.size)
              time.sleep(1)
            elif self.is_rb_board == 1:
              # 画蓝色框
              cv2.rectangle(frame, lingerman_pt1, lingerman_pt2, self.color, 2)
              # 转为灰度图
              lingerman_rect_img = cv2.cvtColor(lingerman_rect_img, cv2.COLOR_BGR2GRAY)
              # 二值化
              lingerman_rect_img[lingerman_rect_img > 255*self.binarization_thres] = 255
              lingerman_rect_img[lingerman_rect_img <= 255*self.binarization_thres] = 0

              rect_img_h, rect_img_w = lingerman_rect_img.shape
              lingerman_blackness = np.sum(lingerman_rect_img == 0) / (rect_img_h * rect_img_w)
              # print("lingerman_blackness", lingerman_blackness)
              # 计算黑度等级
              self.lingerman_darkness = service.darkness_sqrt(lingerman_blackness, self.darkness_level['camera'][self.camera])
              # print("lingerman_level",self.lingerman_darkness)
              if self.lingerman_darkness >= 1:
                self.lingerman_bool = 1
                utils.write_log(str(self.camera), "push_frame 检测到黑度等级>=1,并且是林格曼板")
                print("self.lingerman_bool", self.lingerman_bool)
                scalePix = 10
                print("放大")
                m.move_3d_enlarge(self.filedata, self.client, scalePix, self.result_dn_data, self.size)
                time.sleep(1)
            self.dist_output.write(frame)
            continue
          # 有直线，是林格曼板
          if self.lingerman_bool == 1:
            # self.result_dn_data['board_bool'] = 1 # 找到白板

            # 画蓝色框
            cv2.rectangle(frame, lingerman_pt1, lingerman_pt2, self.color, 2)
            # 转为灰度图
            lingerman_rect_img = cv2.cvtColor(lingerman_rect_img, cv2.COLOR_BGR2GRAY)
            # 二值化
            lingerman_rect_img[lingerman_rect_img > 255*self.binarization_thres] = 255
            lingerman_rect_img[lingerman_rect_img <= 255*self.binarization_thres] = 0

            rect_img_h, rect_img_w = lingerman_rect_img.shape
            lingerman_blackness = np.sum(lingerman_rect_img == 0) / (rect_img_h * rect_img_w)
            print("lingerman_blackness", lingerman_blackness)
            # 计算黑度等级
            self.lingerman_darkness = service.darkness_sqrt(lingerman_blackness, self.darkness_level['camera'][self.camera])
            print("lingerman_level",self.lingerman_darkness)
            self.dist_output.write(frame)
            continue
          
        # 测烟流程
        if self.frame_index and self.now_index % self.darkness_skip_index == 0:
          # 找到白板
          self.result_dn_data['board_bool'] = 1

          # 转灰度
          rect_img = cv2.cvtColor(rect_img, cv2.COLOR_RGB2GRAY)
          # print("first_frame_map: ", first_frame_map)
          # 得出白板区域
          rect_img_a = rect_img * first_frame_map
          # 类型转换
          rect_img_16 = np.array(rect_img_a, dtype='int16')
          first_frame_arr_16 = np.array(first_frame_arr, dtype='int16')

          # 获取黑度差
          rect_img_dst = first_frame_arr_16 - rect_img_16
          # 获取不等于0的数组数量
          now_rect_img_sum = np.sum(rect_img_dst!=0)
          # 求和
          rect_img_copy_sum = rect_img_dst.sum()

          # 每一帧的平均黑度
          if rect_img_copy_sum and now_rect_img_sum:
            rect_img_sum = int( rect_img_copy_sum / now_rect_img_sum )
          else:
            rect_img_sum = 0

          # 临时添加
          blackness_list.append(rect_img_sum)
          if len(blackness_list) > blackness_list_count:
            blackness_list = blackness_list[1:]
          blackness_list.extend([0 for item in range(blackness_list_count - len(blackness_list))])
          frame = draw.draw_axis(frame, {
            "x_arr": (0, 100),
            "y_arr": (0, max(blackness_list) if max(blackness_list) > 10 else 10),
            "data": blackness_list,
            "axis_pos": "left_bottom"})

          # 和第一帧的黑度差
          if self.max_rect_img_sum < rect_img_sum or self.max_darkness_frame == []:
            self.max_rect_img_sum = rect_img_sum
            self.max_darkness_frame = pure_frame

          # if self.max_rect_img_sum > 50:
          #   break
          # 林格曼黑度
          blackness = utils.darkness_level(self.max_rect_img_sum)

          now_blackness = utils.darkness_level(rect_img_sum)
          # 获取最大等级
          if self.result_dn_data['level'] < int(now_blackness):
            self.result_dn_data['level'] = int(now_blackness)
          frame = cv2.putText(frame, 'now darkness: ' + str(rect_img_sum), (20, 80), self.axis_font,self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
          frame = cv2.putText(frame, 'max darkness: ' + str(self.max_rect_img_sum), (20, 100),self.axis_font, self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
          frame = cv2.putText(frame, 'blackness: ' + str(blackness), (20, 120), self.axis_font,self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)
          frame = cv2.putText(frame, 'now blackness: ' + str(now_blackness), (20, 140), self.axis_font,self.axis_y_font_size, self.axis_y_font_color, self.axis_y_font_weight)

          self.diff_black_arr.append(rect_img_sum)
          if len(self.diff_black_arr) > 250:
            self.diff_black_arr = self.diff_black_arr[1:]

          # 将图填充到画面
          rect_img_w = self.filedata['xmax'] - self.filedata['xmin']
          rect_img_h = self.filedata['ymax'] - self.filedata['ymin']
          fillPointXmin, fillPointXmax = self.size[0] - rect_img_w - 30, self.size[0] - 30
          fillPointYmin, fillPointYmax = self.size[1] - rect_img_h - 60, self.size[1] - 60
          tr_fillPointXmin, tr_fillPointXmax = self.size[0] - rect_img_w - 30, self.size[0] - 30
          tr_fillPointYmin, tr_fillPointYmax = 60, rect_img_h + 60

          # diff_img = first_frame_arr_16 - rect_img_16
          diff_img = rect_img_16 - first_frame_arr_16
          diff_img[diff_img>=0] = 255
          diff_img[diff_img<0] += 255
          diff_img = np.array(diff_img, dtype='uint8')

          trect_img = cv2.cvtColor(diff_img, cv2.COLOR_GRAY2BGR)
          tr_first_frame_arr = cv2.cvtColor(first_frame_arr, cv2.COLOR_GRAY2BGR)

          if fillPointXmin > 0 and fillPointXmax < self.size[0] and \
            fillPointYmin > 0 and fillPointYmax < self.size[1]:
            frame[fillPointYmin:fillPointYmax, fillPointXmin:fillPointXmax] = trect_img
            frame[tr_fillPointYmin:tr_fillPointYmax, tr_fillPointXmin:tr_fillPointXmax] = tr_first_frame_arr

          # 写入推理视频
          self.dist_output.write(frame)


  # 发送检测结果
  def send_dn_result(self):
    # 生成图片
    img_filename = str(time.time()) + '.jpg'
    evidence_img_path = os.path.join(var.local_path['keyframe_path'], img_filename)
    if len(self.max_darkness_frame) > 0:
      utils.write_log(str(self.camera), "send_dn_result 生成检出图片")
      cv2.imwrite(evidence_img_path, self.max_darkness_frame)
      self.result_dn_data['evidence_img'].append(img_filename)

    print(self.lingerman_darkness, type(self.lingerman_darkness))
    if self.lingerman_bool == 1:
      self.result_dn_data['level'] = int(self.lingerman_darkness)
      self.result_dn_data['board_bool'] = 1
      utils.write_log(str(self.camera), "林格曼等级lingerman_darkness = "+ str(self.lingerman_darkness))

    # if self.result_dn_data['smoke_change']:
    utils.write_log(str(self.camera), "self.pass_frame_num = "+ str(self.pass_frame_num))
    utils.write_log(str(self.camera), "原来的level = "+ str(self.result_dn_data['level']))
    # if self.pass_frame_num >= 35:  
    #   self.result_dn_data['level'] = 0

    # 判断是否检出黑烟
    if self.result_dn_data['level'] >= 2 and self.lingerman_bool != 1:
      utils.write_log(str(self.camera), "send_dn_result 检出黑烟")
      self.result_dn_data['result'] = 1
    

      
    # 写入redis
    self.data = r.get_values(self.camera)
    self.data['rath_end'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    self.data['rath_board_time'] = round(time.time() - self.start_time,2)
    self.data['filedata'] = {
      "xmin":  0,
      "ymin":  0,
      "xmax":  0,
      "ymax":  0
    }
    self.data['status'] = "rath ending"
    r.set_values(self.camera ,self.data)

    utils.write_log(str(self.camera), "send_dn_result 写入观察redis: ")
    utils.write_log(str(self.camera), self.data)

    rabbit = Rabbit()
    rabbit.create_queue(var.rabbitmq_queue['dn_darkness_result'], self.result_dn_data)
    # 打印日志
    self.temp_write_log(self.result_dn_data)

  def darkness_controll(self, ch, method, properties, body):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    result = json.loads( body.decode() )
    print("darkness: ", result, type(result))
    # 开始检测
    if result['type'] == 'start':
      self.dn_darkness_bool = True
      utils.write_log(str(self.camera), "darkness_controll 开始测烟")

    elif result['type'] == 'stop':
      self.dn_darkness_bool = False
      utils.write_log(str(self.camera), "darkness_controll 结束测烟")


  def temp_write_log(self, content):
    with open("/root/app/logs/rath.log", 'a+') as f:
      now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
      f.write("\n" + str(now_time) + " " + json.dumps(content))

  # 监听黑烟
  def listen_darkness(self):
    rabbit = Rabbit()           # rabbitMQ
    rabbit.consumer(var.rabbitmq_queue['dn_darkness'] + '_' + str(self.camera), self.darkness_controll)

  def run(self):
    threads = [
      threading.Thread(target=Live.read_frame, args=(self,)),
      threading.Thread(target=Live.push_frame, args=(self,)),
      threading.Thread(target=Live.listen_darkness, args=(self,)),
      threading.Thread(target=Live.read_detection, args=(self,)),
    ]
    [thread.setDaemon(True) for thread in threads]
    [thread.start() for thread in threads]
    return threads

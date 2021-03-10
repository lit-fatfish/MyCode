import os, json, time, queue, cv2, threading, socket,math
import subprocess as sp
import numpy as np
from cv2 import cv2


class Live(object):
  def __init__(self, rtmpUrl, camera_path):
    self.frame_queue = queue.Queue(maxsize=1)
    self.command = ""
    self.size = (1280, 720)
    self.fps = 25

    self.rtmpUrl = rtmpUrl
    self.camera_path = camera_path

    self.color = (255, 0, 0)    
                          # 
    self.client = socket.socket(socket.AF_INET,socket.SOCK_STREAM) #声明socket类型，同时生成链接对象
    # self.client.connect(('192.168.31.8',7003)) #建立一个链接，连接到本地的6969端口
    self.client.connect(('172.17.0.1',7003)) #建立一个链接，连接到本地的7003端口
    



  def read_frame(self):
    print("开启推流")
    cap = cv2.VideoCapture(self.camera_path)

    # Get video information
    self.fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    #获取中间点
    

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
      # ret, frame = cap.read()
      # ret, frame = cap.read()
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
    # board_frame_thres = 25

    
    while True:
      if self.frame_queue.empty() != True:
        frame = self.frame_queue.get()
        
        if len(frame) == 0:
          continue
        
        p.stdin.write(frame.tostring())
          
 
  # 运行
  def run(self):
    threads = [
      threading.Thread(target=Live.read_frame, args=(self,)),
      threading.Thread(target=Live.push_frame, args=(self,))
    ]
    [thread.setDaemon(True) for thread in threads]
    [thread.start() for thread in threads]
    return threads



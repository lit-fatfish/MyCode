import multiprocessing as mp
import cv2, threading, time
import numpy as np
import os
import signal

"""
2018-06-03 Yonv1943
2018-06-08 stable, compare the real time frames, and draw the contours of the moving objects
2018-07-02 setattr(), if is_opened
2018-11-24 polygon 
"""

class EdgeDetection(object):
  def __init__(self, img):
    self.background_change_after_read_image_number = 25
    self.img_back = img
    self.img_list = [img for _ in range(self.background_change_after_read_image_number)]
    self.draw_index = 0                 # 检出多少帧
    self.min_thresh = 56.0              # 二值化阈值
    self.min_side_len = int(360/24)     # 最小的边昌
    self.min_side_num = 5               # 至少需要多少个边才判定为轮廓
    self.min_poly_len = int(360/12)     # 多边形周长

    

  def get_polygon_contours(self, img, img_back):
    # img = np.copy(img)
    dif = np.array(img, dtype=np.int16)
    dif = np.abs(dif - img_back)
    dif = np.array(dif, dtype=np.uint8)  # get different

    gray = cv2.cvtColor(dif, cv2.COLOR_BGR2GRAY)  # 转灰度图
    ret, thresh = cv2.threshold(gray, self.min_thresh, 255, 0)  # 二值化
    # thresh = cv2.blur(thresh, (self.thresh_blur, self.thresh_blur))
    thresh = cv2.GaussianBlur(thresh, (9, 9), 0)  # 高斯模糊

    if np.max(thresh) == 0:  # have not different
      contours = []
    else:
      '''
      cv2.findContour:输入的参数
        thresh = 寻找轮廓的图像，
        cv2.RETR_EXTERNAL 表示只检测外轮廓, 
        cv2.CHAIN_APPROX_SIMPLE 压缩水平方向，垂直方向，对角线方向的元素，只保留该方向的终点坐标，例如一个矩形轮廓只需4个点来保存轮廓信息
        返回值：
          contour 返回一个list，list中每个元素都是图像中的一个轮廓，用numpy中的ndarray表示。
      '''
      contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 轮廓检测

      # hulls = [cv2.convexHull(cnt) for cnt, hie in zip(contours, hierarchy[0]) if hie[2] == -1]
      # hulls = [hull for hull in hulls if cv2.arcLength(hull, True) > self.min_hull_len]
      # contours = hulls
      
      '''
      主要功能是把一个连续光滑曲线折线化
      cv2.approxPolyDP:输入参数
        InputArray curve：输入曲线，数据类型可以为vector<Point>。
        double epsilon：判断点到相对应的line segment 的距离的阈值。（距离大于此阈值则舍弃，小于此阈值则保留，epsilon越小，折线的形状越“接近”曲线。）
        bool closed：曲线是否闭合的标志位。
      cv2.arcLength
      计算轮廓周长
      # approxs 里面有n个轮廓
      # len(approx ) 有多少条边
      '''
      approxs = [cv2.approxPolyDP(cnt, self.min_side_len, True) for cnt in contours]  # 填充数据

      approxs = [approx for approx in approxs                             
                  if len(approx) > self.min_side_num and cv2.arcLength(approx, True) > self.min_poly_len]# 只取满足条件的框
      contours = approxs
    return contours

  def main_get_img_show(self, img):
    invade = False
    contours = self.get_polygon_contours(img, self.img_back)

    self.img_list.append(img)
    img_prev = self.img_list.pop(0)

    self.img_back = img \
        if not contours or not self.get_polygon_contours(img, img_prev) \
        else self.img_back

    # show_img = np.array(self.high_light_roi_mat * origin_img, dtype=np.uint8)
    # 绘制多条多边形曲线。
    show_img = cv2.polylines(img, contours, True, (0, 0, 255), 2) if contours else img

    if contours:
      self.draw_index += 1
      invade = True
    print("self.draw_index: ", self.draw_index)
    return show_img, invade

video_path = "D:/Code/demo_code/video/1610082885.254384_source.mp4"

def queue_img_put(q, name, pwd, ip, channel=1):
  # cap = cv2.VideoCapture("rtsp://%s:%s@%s//Streaming/Channels/%d" % (name, pwd, ip, channel))
  # default
  # video_path = "Z:/lex/project/环检相关/video/1.mp4"

  # Ring video
  # video_path = "C:/Users/Administrator/Desktop/test_dir/Ring_video/20200804_104325.mp4"

  # video 2
  # video_path = "Z:/lex/project/环检相关/video/2.mp4"

  # cap = cv2.VideoCapture(0)
  cap = cv2.VideoCapture(video_path)
  while True:
    is_opened, frame = cap.read()
    q.put(frame)
    # q.put(frame) if is_opened else None
    # q.get() if q.qsize() > 1 else None


def queue_img_get(q, window_name):
  index = 0
  frame = q.get()


  # region_of_interest_pts = DrawROI(frame).draw_roi()

  # default
  region_of_interest_pts = np.array([[480, 240], [800, 240], [800, 500], [480, 500]])

  # video1
  # region_of_interest_pts = np.array([[480, 230], [830, 240], [820, 516], [480, 490]])

  # Ring video
  # region_of_interest_pts = np.array([[490, 600], [760, 600], [770, 760], [440, 740]])

  # video 2
  # region_of_interest_pts = np.array([[480, 200], [800, 230], [800, 530], [480, 500]])
  # region_of_interest_pts = [[50, 50], [500, 50], [500, 400], [50, 400], [50, 50]]
  # region_of_interest_pts = [[50, 50], [500, 50], [500, 400], [50, 400], [50, 50]]

  # cv2.namedWindow(window_name, flags=cv2.WINDOW_FREERATIO)
  # frog_eye = EdgeDetection(frame, region_of_interest_pts)
  # 初始化视频
  

  rect_box = {
    "xmin": 480,
    "xmax": 800,
    "ymin": 240,
    "ymax": 500
  }
  cap = cv2.VideoCapture(video_path)

  # Get video information
  fps = int(cap.get(cv2.CAP_PROP_FPS))
  width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
  height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
  
  size = (width, height)
  # 创建 VideoWriter对象
  codec = cv2.VideoWriter_fourcc(*'mp4v')
  name = str(time.time())
  dist_output = cv2.VideoWriter( name + '.mp4', codec, fps, size)

  # Height, Width
  frame = frame[rect_box['ymin']:rect_box['ymax'], rect_box['xmin']:rect_box['xmax']]
  frog_eye = 0
  frog_eye = EdgeDetection(frame)
  print(frog_eye, type(frog_eye))
  cv2.imwrite("init_frame.jpg",frame)
  invade = False
  while True:
    frame = q.get()
    if len(frame) == 0:
      dist_output.release()

      exit(0)


    check_frame = frame[rect_box['ymin']:rect_box['ymax'], rect_box['xmin']:rect_box['xmax']]
    index += 1
    # if index <= 1500:
    #   continue
    frame = cv2.rectangle(frame, (rect_box['xmin'],rect_box['ymin']), (rect_box['xmax'],rect_box['ymax']),(0,0,255),2)
    
    timestart = int(time.time() * 1000)
    img_show, invade = frog_eye.main_get_img_show(check_frame)
    if invade:
      frame = cv2.putText(frame, "invade",(20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0))
    timesend = int(time.time() * 1000)
    frame[rect_box['ymin']:rect_box['ymax'], rect_box['xmin']:rect_box['xmax']] = img_show
    print("index: ", index, "diff time: ", timesend - timestart)
    dist_output.write(frame)
    # cv2.imshow(window_name, frame)
    # cv2.waitKey(1)

def CtrlC():
  #如果用sys.exit()在上层有try的情况下达不到直接结束程序的效果（自行百度）
  os._exit(0)

def run():
  user_name, user_pwd, camera_ip = "admin", "anlly1205", "192.168.31.12"

  mp.set_start_method(method='spawn')  # multi-processing init
  queue = mp.Queue(maxsize=2)
  threads = [
    threading.Thread(target=queue_img_put, args=(queue, user_name, user_pwd, camera_ip)),
    threading.Thread(target=queue_img_get, args=(queue, camera_ip)),
  ]
  [thread.setDaemon(True) for thread in threads]
  [thread.start() for thread in threads]
  return threads



if __name__ == '__main__':
  threads = run()
  while 1:
    time.sleep(1)
    for item in threads:
      if item.isAlive() == False:
        exit(0)

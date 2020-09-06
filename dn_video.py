#coding=utf-8
import os, time, cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import subprocess as sp
import extend.darknet as cnet
from extend.utils import Utils
from extend.variables import Variables


util = Utils()       # 初始化utils
var = Variables()     # 初始化变量


class Detection:
  def __init__(self):
    pass

  # 返回指定classes point
  def res_type_point(self, detections, class_type=''):
    arr = []
    for detection in detections:
      x, y, w, h = detection[2][0], \
                  detection[2][1], \
                  detection[2][2], \
                  detection[2][3]
      xmin, ymin, xmax, ymax = self.convertBack(float(x), float(y), float(w), float(h))
      if detection[0] == bytes(class_type, encoding="utf8"):
        arr.append({
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax
        })
      if class_type == '':
        arr.append({
            "xmin": xmin,
            "ymin": ymin,
            "xmax": xmax,
            "ymax": ymax
        })
    return arr

  def paint_chinese_opencv(self, im, chinese, pos, color, fontSize):
    img_PIL = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
    font = ImageFont.truetype('/root/app/NotoSansCJK-Bold.ttc', fontSize)
    fillColor = color #(255,0,0)
    position = pos #(100,100)
    if not isinstance(chinese,str):
      chinese = chinese.decode('utf-8')
    draw = ImageDraw.Draw(img_PIL)
    draw.text(position, chinese, font=font, fill=fillColor)
    img = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
    return img

  def convertBack(self, x, y, w, h):
    xmin = int(round(x - (w / 2)))
    xmax = int(round(x + (w / 2)))
    ymin = int(round(y - (h / 2)))
    ymax = int(round(y + (h / 2)))
    return xmin, ymin, xmax, ymax

  def replace_tag(self, model_name):
    # 框的颜色  红(255, 0, 0)   绿(0, 255, 0)  蓝(0, 0, 255)  黄色(255, 255, 0)   深天蓝(0, 191, 255)
    color = (255, 0, 0)
    txt_color = (255, 255, 255)
    bg_color = (255, 0, 0)
    text = ''

    if model_name == b'person':
      text = "不安全"
      color = (255, 165, 0) # 橙色
      bg_color = (255, 165, 0)
    elif model_name == b'hat':
      text = "安全"
      color = (0, 255, 0)
      bg_color = (0, 255, 0)
    elif model_name == b'smoke':
      text = "烟"
    elif model_name == b'dust':
      text = "扬尘"
    elif model_name == b'truck':
      text = "大车"
      color = (0, 191, 255) # 深蓝色
      bg_color = (0, 191, 255)
    elif model_name == b'shovel':
      text = "铲车"
      color = (0, 191, 255)
      bg_color = (0, 191, 255)
    elif model_name == b'digger':
      text = "挖掘机"
      color = (0, 191, 255)
      bg_color = (0, 191, 255)
    elif model_name == b'crane':
      text = "吊机"
      color = (0, 191, 255)
      bg_color = (0, 191, 255)
    elif model_name == b'piling':
      text = "打桩机"
      color = (0, 191, 255)
      bg_color = (0, 191, 255)
    return color, txt_color, bg_color, text

  def cvDrawBoxes(self, detections, img):
    for detection in detections:
      model_name = detection[0]
      color, txt_color, bg_color, text = self.replace_tag(model_name)
      x, y, w, h = detection[2][0],\
        detection[2][1],\
        detection[2][2 ],\
        detection[2][3]
      xmin, ymin, xmax, ymax = self.convertBack(
        float(x), float(y), float(w), float(h))
      pt1 = (xmin, ymin)
      pt2 = (xmax, ymax)

      cv2.rectangle(img, pt1, pt2, color, 2)
      point = {'x': xmin, 'y': ymin}
      ymin, xmax, ymax = ymin - 24, xmin + 20*len(text), ymin
      points = [
        (xmin, ymin), 
        (xmin, ymax), 
        (xmax, ymax), 
        (xmax, ymin)
      ]
      img = cv2.fillPoly(img, [np.array(points)], bg_color)
      img = self.paint_chinese_opencv(img, text, (point['x'] + 2*len(text), point['y'] - 24), txt_color, 16)
    return img

  # 坐标转换
  def convert_point(self, now_frame_count, detections, check_tag):
    res_arr = {"framenum": now_frame_count, "list": []}
    for detection in detections:
      x, y, w, h = detection[2][0], \
                  detection[2][1], \
                  detection[2][2], \
                  detection[2][3]
      xmin, ymin, xmax, ymax = self.convertBack(float(x), float(y), float(w), float(h))
      if check_tag == detection[0]:
        res_arr["list"].append({
          'tag': str(detection[0], encoding = "utf-8"),
          "x1": int(xmin),
          "y1": int(ymin),
          "x2": int(xmax),
          "y2": int(ymax)
        })
    return res_arr

  # 判断两个矩形是否相交
  def mat_inter(self, box1, box2):
    # 判断两个矩形是否相交
    # box=(xA,yA,xB,yB)
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = box2

    lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)
    ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)
    sax = abs(x01 - x02)
    sbx = abs(x11 - x12)
    say = abs(y01 - y02)
    sby = abs(y11 - y12)
    if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:
        return True
    else:
        return False

  # 坐标
  def sqrt_distance(self, truck_arr, smoke_arr):
    is_mater = False
    for smoke_item in smoke_arr:
      for truck_item in truck_arr:
        smoke_r1 = (smoke_item['xmin'], smoke_item['ymin'], smoke_item['xmax'], smoke_item['ymax'])
        truck_r1 = (truck_item['xmin'], truck_item['ymin'], truck_item['xmax'], truck_item['ymax'])
        if self.mat_inter(smoke_r1, truck_r1):
          is_mater = True
          return is_mater
    return is_mater
  
  def std_ffmpeg(self, output_file, size, fps):
    ffmpeg = 'ffmpeg'
    dimension = '{}x{}'.format(size[0], size[1])
    f_format = 'bgr24' # remember OpenCV uses bgr format
    fps = str(25)
    command = [ffmpeg,
        '-y',
        '-f', 'rawvideo',
        '-vcodec','rawvideo',
        '-s', dimension,
        '-pix_fmt', 'bgr24',
        '-r', fps,
        '-i', '-',
        '-an',
        '-c:v', 'libx264',
        '-b:v', '4000k',
        output_file]
    return command

  def load_models(self, model_config):
    netMain = None
    metaMain = None
    altNames = None

    configPath = model_config['cfg']
    weightPath = model_config['weights']
    metaPath = model_config['data']

    if not os.path.exists(configPath):
        raise ValueError("Invalid config path `" +
                         os.path.abspath(configPath)+"`")

    if not os.path.exists(weightPath):
        raise ValueError("Invalid weight path `" +
                         os.path.abspath(weightPath)+"`")

    if not os.path.exists(metaPath):
        raise ValueError("Invalid data file path `" +
                         os.path.abspath(metaPath)+"`")

    if netMain is None:
        netMain = cnet.load_net_custom(configPath.encode(
            "ascii"), weightPath.encode("ascii"), 0, 1)  # batch size = 1
    
    if metaMain is None:
        metaMain = cnet.load_meta(metaPath.encode("ascii"))

    if altNames is None:
        try:
            with open(metaPath) as metaFH:
                metaContents = metaFH.read()
                import re
                match = re.search("names *= *(.*)$", metaContents,
                                  re.IGNORECASE | re.MULTILINE)
                if match:
                    result = match.group(1)
                else:
                    result = None
                try:
                    if os.path.exists(result):
                        with open(result) as namesFH:
                            namesList = namesFH.read().strip().split("\n")
                            altNames = [x.strip() for x in namesList]
                except TypeError:
                    pass
        except Exception:
            pass

    return {
      'net': netMain,
      'meta': metaMain,
      'alt': altNames
    }

  def detection_video(self, params):
    frame = params['frame']
    model_conf = params['model_conf']
    darknet_image = params['darknet_image']
    size = params['size']
    thresh = params['thresh']

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cnet.copy_image_from_bytes(darknet_image, frame_rgb.tobytes())
    detections = cnet.detect_image(model_conf['net'], model_conf['meta'], darknet_image, thresh=float(thresh))
    # frame_rgb = self.cvDrawBoxes(hat_detections, frame_rgb)

    return detections


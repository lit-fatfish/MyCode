# 获取摄像机当前的图片

import cv2, time

rtsp_url = "/dev/video10" 
rtsp_url = "rtsp://192.168.31.8/ice_box" 
cap = cv2.VideoCapture(rtsp_url)


ret, frame = cap.read()
if ret: 
  cv2.imwrite(str(time.time())+'.jpg', frame)


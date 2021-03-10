import os, time, sys
from darkness_live import Live

# # 推理后的rtsp流
rtmpUrl = "rtsp://192.168.31.8:554/dn_201"
# # 相机的rtsp流
camera_path = "rtsp://admin:anlly1205@192.168.31.12/h264/main/sub/av_stream"
camera_path = "/dev/video10"
rtmpUrl = "rtsp://192.168.31.8:554/ice_box"




live = Live(rtmpUrl, camera_path)
threads = live.run()

while 1:
  time.sleep(1)
  for item in threads:
    if item.isAlive() == False:
      exit(0)


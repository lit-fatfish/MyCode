import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils import Utils
# 1.1对视频进行动态直方图绘制

utils = Utils()
video_src_path = "./src_file/1.2.mp4"
video_dst_path = "./dst_file/1.2.mp4"


board_arr = {
    "xmin": 875,
    "ymin": 244,
    "xmax": 1125,
    "ymax": 483,
}


cap = cv2.VideoCapture(video_src_path)

#获取视频帧率
fps_video = cap.get(cv2.CAP_PROP_FPS)
print("fps_video", fps_video)
#设置写入视频的编码格式
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
#获取视频宽度
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#获取视频高度
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(frame_width, frame_height)
videoWriter = cv2.VideoWriter(video_dst_path, fourcc, fps_video, (frame_width, frame_height))

frame_id = 0

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        if len(frame) == 0:
            continue
        img = frame.copy()
        print(img.shape, frame.shape)
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        board_area = img_gray[board_arr["ymin"]:board_arr["ymax"], board_arr["xmin"]:board_arr["xmax"]]
        
        hist_board = cv2.calcHist([board_area],[0], None, [256], [0, 256])

        frame = utils.draw_axis(frame, hist_board, (85, frame.shape[0]-100), [], int(max(hist_board)))
        frame[0:board_area.shape[0], img.shape[1]-board_area.shape[1]-50:img.shape[1]-50] = cv2.cvtColor(board_area, cv2.COLOR_GRAY2BGR)
        frame = cv2.rectangle(frame, (board_arr['xmin'], board_arr['ymin']), (board_arr['xmax'], board_arr['ymax']), (0,255,0), 2)
        frame_id += 1
        
        videoWriter.write(frame)

    else:
        videoWriter.release()
        break

print("frame", frame_id)


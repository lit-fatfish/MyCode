# 输入推理视频
# 剪辑一段出来
# 将剪辑出来的文字加上文字
# 一种是安全帽，一种是烟

import cv2 
import os, sys
import numpy as np
from PIL import Image, ImageFont, ImageDraw


# 获取参数

src_video = sys.argv[1]
dst_video = sys.argv[2]
event_type = sys.argv[3]

print("src_video=", src_video)
print("dst_video=", dst_video)
print("event_type=", event_type)

try:
    num = sys.argv[4]
    print("num=", num)
except:
    print("no four argv")




# exit(0)
def paint_chinese_opencv(im,chinese,pos,color, fontsize):
  img_PIL = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
  font = ImageFont.truetype('NotoSansCJK-Bold.ttc', fontsize)
  fillColor = color #(255,0,0)
  position = pos #(100,100)
  if not isinstance(chinese,str):
      chinese = chinese.decode('utf-8')
  draw = ImageDraw.Draw(img_PIL)
  draw.text(position, chinese, font=font, fill=fillColor)
  img = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
  return img

# 对烟事件加文字
def tranform_video_for_smoke(src_filename, dst_filename, number_plate):
    cap = cv2.VideoCapture(src_filename)

    #获取视频帧率
    fps_video = cap.get(cv2.CAP_PROP_FPS)
    print("fps_video", fps_video)
    #设置写入视频的编码格式
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #获取视频宽度
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #获取视频高度
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    videoWriter = cv2.VideoWriter(dst_filename, fourcc, fps_video, (frame_width, frame_height))

    frame_id = 0
    event_height = frame_height - 80
    num_height = frame_height - 50

    print("event_height ",event_height)
    print("num_height ",num_height)
    full_number = "违规机械编码：" + number_plate

    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            # frame = paint_chinese_opencv(frame, "云景安全帽事件", (20,670), (255, 255, 255), 24)

            frame = paint_chinese_opencv(frame, "云景黑烟事件", (20,event_height), (255, 255, 255), 24)
            frame = paint_chinese_opencv(frame, full_number , (20,num_height), (255, 255, 255), 24)
            frame_id += 1
            
            videoWriter.write(frame)
        else:
            videoWriter.release()
            break
    
    return dst_filename

# 对安全帽事件加文字
def tranform_video_for_hat(src_filename, dst_filename):
    cap = cv2.VideoCapture(src_filename)

    #获取视频帧率
    fps_video = cap.get(cv2.CAP_PROP_FPS)
    print("fps_video", fps_video)
    #设置写入视频的编码格式
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    #获取视频宽度
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    #获取视频高度
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    videoWriter = cv2.VideoWriter(dst_filename, fourcc, fps_video, (frame_width, frame_height))

    frame_id = 0

    event_height = frame_height - 50


    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            frame = paint_chinese_opencv(frame, "云景安全帽事件", (20,event_height), (255, 255, 255), 24)
            frame_id += 1
            
            videoWriter.write(frame)
        else:
            videoWriter.release()
            break
    
    return dst_filename

# tmp_filename = "temp.mp4"

# cut_video_cmd = "ffmpeg -i " + src_video + " -ss " + str(start_time) + " -t  " + str(end_time) + " -c copy -f mp4 -y " + tmp_filename
# val = os.system(cut_video_cmd)

# os.popen(cut_video_cmd)

if event_type == "smoke":
    print("run smoke add text")
    print(tranform_video_for_smoke(src_video, dst_video, num))
    
    
elif event_type == "hat":
    print("run hat add text")
    tranform_video_for_hat(src_video, dst_video)




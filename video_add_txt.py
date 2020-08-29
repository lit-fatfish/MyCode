import os, cv2
import numpy as np
from PIL import Image, ImageFont, ImageDraw

# 读取一个视频，加框和加参数


video_src_path = "/home/anlly/workspace/nas_project/keimy/data_building/20200827_building/hat/record_miku5_20200827103425.mp4"

video_dst_path = "/home/anlly/workspace/nas_project/keimy/data_building/20200827_building/hat_dist/record_miku5_20200827103425.mp4"



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

if not os.path.exists(video_src_path):
    print("video not found")
    exit(0)

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

videoWriter = cv2.VideoWriter(video_dst_path, fourcc, fps_video, (frame_width, frame_height))

frame_id = 0

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        frame = paint_chinese_opencv(frame, "云景安全帽事件", (20,670), (255, 255, 255), 24)

        # frame = paint_chinese_opencv(frame, "云景黑烟事件", (20,640), (255, 255, 255), 24)
        # frame = paint_chinese_opencv(frame, "云景黑烟事件", (20,640), (255, 255, 255), 24)
        # frame = paint_chinese_opencv(frame, "违规车牌编码：X-KE000504", (20,670), (255, 255, 255), 24)
        frame_id += 1
        
        # cv2.putText(frame, str(frame_id), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (55,255,155), 2)

        # pt1 = (504, 491)    # 左上角
        # pt2 = (569, 519)    # 右下角
        # color = (0, 0, 255) # 颜色

        # cv2.rectangle(frame, pt1, pt2, color, 2)
        


        videoWriter.write(frame)
    else:
        videoWriter.release()
        break

print("frame", frame_id)




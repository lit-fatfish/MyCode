# 通过pid文件获取到框的数据，并且添加到视频中
import os, cv2
# import darknet as dn
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import json

pid_path = "/home/anlly/machine_learning/docker/flask/store/2ec336fc-e789-11ea-8d39-536327161d36.json"

video_src_path = "/home/anlly/workspace/nas_project/frank/model_test/video_test/src/test.mp4"
video_dst_path = "/home/anlly/workspace/nas_project/frank/model_test/video_test/dst/test_0827_3.mp4"




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

def read_jsonfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

            return json_data
    else:
        # 文件名不存在，写入日志
        print("文件不存在")
        return False

print("hello")
# exit(0)


# code start

# read pid and get useful frame 
pid_dic = read_jsonfile(pid_path)

print(pid_dic)


frame_list = []

for item in pid_dic["metadata"]:
    # print(item)
    print(pid_dic["metadata"][item])
    metadata = pid_dic["metadata"][item]
    print(metadata["z"][0])
    # exit(0)
    frame_num = int(metadata["z"][0]*1000 / int(1000 / 25))
    frame_list.append({
        "frame": frame_num,
        'x': metadata['xy'][1],
        'y': metadata['xy'][2],
        'w': metadata['xy'][3],
        'h': metadata['xy'][4],
        'tag': metadata['av']["2"]
    })
# frame_list.append

for temp in frame_list:
    print(temp)


# exit(0)



## video process start
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
        frame = paint_chinese_opencv(frame, "云景黑烟事件", (20,640), (255, 255, 255), 24)
        frame = cv2.putText(frame, str(frame_id), (30, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (55,255,155), 2)
        for item in frame_list:
            # print(item)
            if frame_id in item.values():
                print("ok", frame_id)
                xmin = int(item["x"])
                xmax = int(item["w"]) + xmin
                ymin = int(item["y"])
                ymax = int(item["h"]) + ymin
            
                pt1 = (xmin, ymin)    # 左上角    xmin ymin
                pt2 = (xmax, ymax)    # 右下角    xmax ymax
                print(pt1)
                print(pt2)
                color = (0, 0, 255) # 颜色

                frame = cv2.rectangle(frame, pt1, pt2, color, 2)

                txt_color = (255, 255, 255) # 字体颜色
                text = "不安全"
                color = (255, 165, 0)
                bg_color = (255, 165, 0)

                point = {'x': xmin, 'y': ymin}
                ymin, xmax, ymax = ymin - 24, xmin + 20*len(text), ymin
                points = [
                    (xmin, ymin), 
                    (xmin, ymax), 
                    (xmax, ymax), 
                    (xmax, ymin)
                ]
                frame = cv2.fillPoly(frame, [np.array(points)], bg_color)
                frame = paint_chinese_opencv(frame, text, (point['x'] + 2*len(text), point['y'] - 24), txt_color, 16)
                

        frame_id += 1
        


        
        videoWriter.write(frame)

    else:
        videoWriter.release()
        break

print("frame", frame_id)

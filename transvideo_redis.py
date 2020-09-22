# 输入推理视频
# 剪辑一段出来
# 将剪辑出来的文字加上文字
# 一种是安全帽，一种是烟

import cv2 
import os, sys, time
import numpy as np
from PIL import Image, ImageFont, ImageDraw
from extend.redis_tools import RedisTools


# # 获取参数

# src_video = sys.argv[1]
# dst_video = sys.argv[2]
# event_type = sys.argv[3]

# print("src_video=", src_video)
# print("dst_video=", dst_video)
# print("event_type=", event_type)

# try:
#     num = sys.argv[4]
#     print("num=", num)
# except:
#     print("no four argv")




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
def tranform_video_for_smoke(src_filename, dst_filename, title, number_plate):
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

            frame = paint_chinese_opencv(frame, title , (20,event_height), (255, 255, 255), 24)
            frame = paint_chinese_opencv(frame, full_number , (20,num_height), (255, 255, 255), 24)
            frame_id += 1
            
            videoWriter.write(frame)
        else:
            videoWriter.release()
            break
    
    return dst_filename

# 对安全帽事件加文字
def tranform_video_for_hat(src_filename, dst_filename, title):
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
            frame = paint_chinese_opencv(frame, title, (20,event_height), (255, 255, 255), 24)
            frame_id += 1
            
            videoWriter.write(frame)
        else:
            videoWriter.release()
            break
    
    return dst_filename



# redis init
r = RedisTools('redis_data', 6379, "anlly12345", 0)

# r.write_queue("cutVideoList", "hello world")
while True:

    time.sleep(1)

    # 读队列cutVideoList
    cutvideo_zset = r.read_queue("cutVideoList")
    print("cutvideo_zset=",cutvideo_zset)
    if cutvideo_zset:

        cutvideo_key = "cut_info:" + str(cutvideo_zset)
        print("cutvideo_key", cutvideo_key)

        # 读取键值对
        cutvideo_values = r.get_values(cutvideo_key)
    
        # 假如数据存在
        if cutvideo_values:
            print("in cut_video process")
            src_video = cutvideo_values["src_video"]
            dst_video = cutvideo_values["dst_video"]
            start_time = cutvideo_values["start_time"]
            time_lenght = cutvideo_values["time_lenght"]
            # status = cutvideo_values["status"]
            # 执行cut视频程序
            cut_video_cmd = "ffmpeg  -ss " + str(start_time) + " -t  " + str(time_lenght) + " -i " + src_video  + " -f mp4 -y " + dst_video
            val = os.system(cut_video_cmd)
            r.remove_queue("cutVideoList", cutvideo_zset)
            if os.path.exists(dst_video):
                # 文件存在，status = 2 成功
                cutvideo_values["status"] = 2

                move_file_cmd = "mv " + dst_video + " " + src_video
                val = os.system(move_file_cmd)
                
                
            else:
                cutvideo_values["status"] = 1

            # 回写
            r.set_values(cutvideo_key, cutvideo_values)
            # r.write_queue("cutVideoResultList", cutvideo_zset)

    
    # 读队列transformVideoList
    transvideo_zset = r.read_queue("transformVideoList")
    print("transvideo_zset=",transvideo_zset)
    if transvideo_zset:

        transvideo_key = "trans_info:" + str(transvideo_zset)
        print("transvideo_key", transvideo_key)

        # 读取键值对
        transvideo_values = r.get_values(transvideo_key)
        # 假如数据存在
        if transvideo_values:
            print("in transform_video process")
            src_video = transvideo_values["src_video"]
            dst_video = transvideo_values["dst_video"]

            title = transvideo_values["title"]
            number_plate = transvideo_values["number_plate"]
            if title:
                if number_plate:
                    # 黑烟事件
                    print("smoke")
                    tranform_video_for_smoke(src_video, dst_video, title, number_plate)
                else:
                    # 其它事件
                    print("other")
                    tranform_video_for_hat(src_video, dst_video, title)
                
                # 转码
                transform_cmd = "nohup ffmpeg -i " + dst_video + " -c:v libx264 -y " + src_video + " && rm " + dst_video + " &"
                os.system(transform_cmd)

                


                # move_file_cmd = "mv " + dst_video + " " + src_video
                # val = os.system(move_file_cmd)

            # 移除队列中的文件
            r.remove_queue("transformVideoList", transvideo_zset)
            # 删除键值对
            r.remove_key(transvideo_key)
        
        else:
            # 键值对不存在的时候，删除队列
            r.remove_queue("transformVideoList", transvideo_zset)

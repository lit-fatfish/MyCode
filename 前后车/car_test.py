import cv2, os, sys, json
import numpy as np



video_full_path = r"D:\Code\MyCode\前后车\小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8[4]\小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8.wh264"



cap = cv2.VideoCapture(video_full_path)

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
videoWriter = cv2.VideoWriter('test.mp4', fourcc, fps_video, (frame_width, frame_height))

frame_id = 0

threshold = 40
min_thresh = 56
min_side_len = int(360/24) 
min_side_num = 5 
min_poly_len = int(360/12)
es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 4))
while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        if len(frame) == 0:
            continue
        frame_id +=1 
        if frame_id == 1:
            previous = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            print(previous.shape)
            # previous = np.zeros((1080,1920))
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # 转换成灰度图
        gray = cv2.absdiff(gray, previous)  # 计算绝对值差
        gray = cv2.medianBlur(gray, 3)  # 中值滤波
        
        ret, mask = cv2.threshold(
                gray, threshold, 255, cv2.THRESH_BINARY)
        mask = cv2.erode(mask, es, iterations=1)
        mask = cv2.dilate(mask, es, iterations=1)

        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # 轮廓检测

        approxs = [cv2.approxPolyDP(cnt, min_side_len, True) for cnt in contours]  # 填充数据

        approxs = [approx for approx in approxs                             
                    if len(approx) > min_side_num and cv2.arcLength(approx, True) > min_poly_len]# 只取满足条件的框
        contours = approxs

        poly_img =  cv2.polylines(frame, contours, True, (255, 255, 255), 2)
        


        cv2.imwrite("test.jpg", mask)
        cv2.imshow('src', frame)  # 在window上显示图片
        cv2.imshow('mask', mask)  # 边界
        cv2.waitKey()
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2RGB)
        videoWriter.write(mask)

    else:
        videoWriter.release()
        cv2.destroyAllWindows()
        break

print("frame", frame_id)
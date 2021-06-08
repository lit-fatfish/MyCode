import cv2, os, json

data_path = r"D:\Code\MyCode\前后车\小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8[4]"

video_full_path = os.path.join(data_path, '小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8.wh264')

json_full_path = os.path.join(data_path, '小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8.info.txt')


def read_jsonfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

            return json_data
    else:
        # 文件名不存在，写入日志
        print("文件不存在")
        return False

json_data = read_jsonfile(json_full_path)


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
# videoWriter = cv2.VideoWriter(video_dst_path, fourcc, fps_video, (frame_width, frame_height))

frame_id = 0

# while (cap.isOpened()):
#     ret, frame = cap.read()
#     if ret == True:
#         if len(frame) == 0:
#             continue
#         frame_id += 1
#         if frame_id == json_data['appearframenum']:
#             arr = json_data['stuPlateRect']
#             x = arr['fX'] * frame_width
#             y = arr['fY'] * frame_height 
#             w = arr['fWidth'] * frame_width
#             h = arr['fHeight'] * frame_height 
#             print(arr)
#             print(x, y, w, h)
#             xmin = int(x)
#             ymin = int(y)
#             xmax = xmin + int(w)
#             ymax = ymin + int(h)
#             new_img = frame[ymin:ymax, xmin:xmax]
#             cv2.imwrite("frame.jpg", frame)
#             cv2.imwrite("new_img.jpg", new_img)
#         # videoWriter.write(frame)

#     else:
#         # videoWriter.release()
#         break

print("frame", frame_id)

# print(json_data)
print(json_data['appearframenum'])
print(json_data['byDriveChan'])
print(json_data['byDriveChan'])


# 前车图片
print(json_data['lstforward'][0]['imagePath'])

lists = os.listdir(data_path)
print(os.listdir(data_path))

for item in lists:
    # print(item)
    if item in json_data['lstforward'][0]['imagePath']:
        print(item)
        print(os.path.join(data_path, item))
        if os.path.exists(os.path.join(data_path, item)):
            print('存在')
        img_src = cv2.imread(r'D:\Code\MyCode\前后车\小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8[4]\小榄镇小榄大道中1_20210408_080312_353_L02_蓝粤Y669C8_forward01.jpg')
        print(img_src)
        arr = json_data['lstforward'][0]['stuPlateRect']
        x = arr['fX'] * frame_width
        y = arr['fY'] * frame_height 
        w = arr['fWidth'] * frame_width
        h = arr['fHeight'] * frame_height 
        print(arr)
        print(x, y, w, h)
        xmin = int(x)
        ymin = int(y)
        xmax = xmin + int(w)
        ymax = ymin + int(h)
        new_img = img_src[ymin:ymax, xmin:xmax]
        cv2.imwrite("01车牌.jpg", new_img)
cv2.waitKey()
cv2.destroyAllWindows()
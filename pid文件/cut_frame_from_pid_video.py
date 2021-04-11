### 对pid文件中的视频进行裁剪


import os, cv2, json
import numpy as np
import urllib.parse


pid_path = "/home/anlly/train/flask/store/028575f4-99aa-11eb-9787-0242ac120005.json"

img_path = "/mnt/softdata/frank/img/temp_test" 



def read_jsonfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

            return json_data
    else:
        # 文件名不存在，写入日志
        print("文件不存在")
        return False


pid_dic = read_jsonfile(pid_path)

video_list = {}


# 1、读取metadata
for item in pid_dic["metadata"]:
    # print(item)
    # print(pid_dic["metadata"][item])
    metadata = pid_dic["metadata"][item]
    # 视频
    if metadata['z']:
        pass
        vid = metadata['vid']
        arr = video_list.get(vid, [])
        frame_num = int(metadata["z"][0]*1000 / int(1000 / 25))
        data = {
            "frame": frame_num,
            'x': metadata['xy'][1],
            'y': metadata['xy'][2],
            'w': metadata['xy'][3],
            'h': metadata['xy'][4],
            'tag': metadata['av']["2"]
        }
        arr.append(data)
        video_list[vid] = arr
    else:
        # # 图片
        pass
        vid = metadata["vid"]
        data = {
            'x': metadata['xy'][1],
            'y': metadata['xy'][2],
            'w': metadata['xy'][3],
            'h': metadata['xy'][4],
            'tag': metadata['av']["2"]
        }
        tag_name = pid_dic["attribute"]["2"]["options"][data['tag']]    
        # dst_floder = os.path.join(img_path, tag_name)
        # if not os.path.exists(dst_floder):
        #     os.makedirs(dst_floder)
        # 根据图片写入原来的地址
        img_path = urllib.parse.unquote(pid_dic['file'][vid]['fname'])
        img_full_path = os.path.join("/mnt/softdata", img_path.split('user')[1][1:])
        if not os.path.exists(img_full_path):
            continue
        if not (data['x'] < 10 or data['y'] < 10 or data['w'] < 10 or data['h'] < 10):
            img = cv2.imread(img_full_path) 
            xmin = int(data['x'])
            ymin = int(data['y'])
            xmax = int(data['x'] + data['w'])
            ymax = int(data['y'] + data['h'])
            # 图片的剪切 
            new_img = img[ymin:ymax, xmin:xmax]
            # 存放在原来的目录下
            img_path = os.path.split(img_full_path)[0]
            dst_img_path = os.path.join(img_path, "head.jpg")

            cv2.imwrite(dst_img_path, new_img)



# 2、处理视频文件数据


# num, 字典的键
video_id = 0

print("video_list", video_list)

for index,num in enumerate(video_list):
    pass
    video_path = urllib.parse.unquote(pid_dic['file'][num]['fname'])
    video_full_path = os.path.join("/mnt/softdata", video_path.split('user')[1][1:])
    print("video_full_path", video_full_path)
    video_name = os.path
    cap = cv2.VideoCapture(video_full_path)
    video_id += 1
    frame_id = 0
    img_id = 0
    # print(video_list[num])
    # exit(0)
    while (cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            for index1,item in enumerate(video_list[num]):
                # print(item)
                tag_name = pid_dic["attribute"]["2"]["options"][video_list[num][index1]['tag']] 

                if frame_id in item.values():
                    if tag_name == "tc":
                        continue
                    print("ok", frame_id)
                    xmin = int(item["x"])
                    xmax = int(item["w"]) + xmin
                    ymin = int(item["y"])
                    ymax = int(item["h"]) + ymin
                
                    pt1 = (xmin, ymin)    # 左上角    xmin ymin
                    pt2 = (xmax, ymax)    # 右下角    xmax ymax
                    if not (xmin < 10 or xmax < 10 or ymin < 10 or ymax < 10):
                        img_id += 1
                        new_img = frame[ymin:ymax, xmin:xmax]
                        img_path = os.path.split(video_full_path)[0]
                        dst_img_path = os.path.join(img_path, "tail"+str(img_id)+".jpg")
                        cv2.imwrite(dst_img_path, new_img)
            frame_id += 1
            
        else:
            break




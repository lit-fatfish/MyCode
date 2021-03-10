# 根据pid中的数据和框，读取出框的位置，然后剪切图片，保存在相应的位置

import os, cv2
# import darknet as dn
import numpy as np
from PIL import Image, ImageFont, ImageDraw
import json

# pid_path = "/home/anlly/train/flask/store/ba10d3c0-3fa1-11eb-80f2-0242ac120003.json"
'''
【1级】pid：b14a5ac6-5fa5-11eb-9f6e-0242ac120005_1
【2级】pid：f9ceb1a2-5fa5-11eb-ab09-0242ac120005_1
【3级】pid：289e609a-5fa6-11eb-a7c0-0242ac120005_1
【4级】pid：6081ace2-5fa6-11eb-9543-0242ac120005_1
'''

'''
【1级】pid：b14a5ac6-5fa5-11eb-9f6e-0242ac120005
【2级】pid：f9ceb1a2-5fa5-11eb-ab09-0242ac120005
【3级】pid：289e609a-5fa6-11eb-a7c0-0242ac120005
【4级】pid：6081ace2-5fa6-11eb-9543-0242ac120005
'''
pid_path = "/home/anlly/train/flask/store/6081ace2-5fa6-11eb-9543-0242ac120005_1.json"
# board_level = "3"
img_path = "/mnt/softdata/frank/model_data/img/20210206" 


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

# code start

# read pid and get useful frame 
pid_dic = read_jsonfile(pid_path)

# print(pid_dic)


'''
思路：
    通过读取metadata 里面的数据可以读取到框的数据和第几个图片的文件位置"file"
    file 里面可以拿到图片的位置，拼接，然后保存到一个新的位置
    
'''


for item in pid_dic["metadata"]:
    # print(item)
    # print(pid_dic["metadata"][item])
    metadata = pid_dic["metadata"][item]
    vid = metadata["vid"]
    data = {
        'x': metadata['xy'][1],
        'y': metadata['xy'][2],
        'w': metadata['xy'][3],
        'h': metadata['xy'][4],
        'tag': metadata['av']["2"]
    }
    tag_name = pid_dic["attribute"]["2"]["options"][data['tag']]    
    dst_floder = os.path.join(img_path, tag_name)
    if not os.path.exists(dst_floder):
        os.makedirs(dst_floder)

    # print(tag_name,data['tag'])

    print(data)
    if not (data['x'] < 10 or data['y'] < 10 or data['w'] < 10 or data['h'] < 10):
        # print(pid_dic["file"][vid]['fname'])
        if pid_dic["file"][vid]['fname'].endswith('jpg'):
            src_img_path = "/mnt/softdata/" + pid_dic["file"][vid]['fname'][17:]
            img = cv2.imread(src_img_path)

            temp = src_img_path.strip().split('/')
            file_name = temp[-1]
            dst_img_path = os.path.join(dst_floder,tag_name + "_" + file_name)
            xmin = int(data['x'])
            ymin = int(data['y'])
            xmax = int(data['x'] + data['w'])
            ymax = int(data['y'] + data['h'])

            new_img = img[ymin:ymax, xmin:xmax]
            
            print(src_img_path)
            # dst_img_path = os.path.join(img_path, vid + ".jpg")
            cv2.imwrite(dst_img_path, new_img)
            print(dst_img_path)
        # break




# list.txt 生成一个xxx.json文件
# 思路
# 读取list文件，然后根据文件中的路径去读取图片和txt文件夹
# 根据这些文件配置文件夹
# 需要配置的文件有
# project
# config
# attribute
# file
# metadata
# view

# 有需要循环的地方
# project -> vidlist["1","2","3","..."]
# file {"1"{ fid/fname/type/loc/src  } "2"{}}
# metadata:{"1_xxxxx":{},"2_xxxxxx":{}}
# view:{"1"{}}


# 生成一个字典
# 循环实现的流程
# 读取txt中的每一行获取到文件名，获取两个问价的位置和文件名
# 读取图片获取到图片的大小，
# 根据需要生成的数据要写代码，先把数据都准备好
# 1、文件名可以直接访问的数据
# 2、根据格式填充数据，
# 3、index增加
# 循环结束写入，生成数据

# list_file_path


# json_file_path


import os
import platform
from datetime import date
import json
import uuid
import time
from PIL import Image

if platform.system() == 'Windows':
    list_file_path = "new_list.txt"
    json_file_path = "."
elif platform.system() == 'Linux':
    list_file_path = "/home/anlly/workspace/rtx_train_data/truck/truck_20200509_new/list.txt"
    json_file_path = "/home/anlly/machine_learning/tag_test/json"



def read_list_file(list_name, save_position):
    if not os.path.exists(list_name):
        print("file not found,")
        return False
    pid_name = str(uuid.uuid4())
    pid_json_data = {
        "project": {
            "pid": pid_name,
            "rev": "__VIA_PROJECT_REV_ID__",
            "rev_timestamp": "__VIA_PROJECT_REV_TIMESTAMP__",
            "pname": "\u51b0\u67dc\u6d4b\u8bd5",
            "creator": "VGG Image Annotator (http://www.robots.ox.ac.uk/~vgg/software/via)",
            "created": int(time.time()),
            "vid_list":[]
            
        },
        "config": {
            "file": {
                "loc_prefix": {
                    "1": "",
                    "2": "",
                    "3": "",
                    "4": ""
                }
            },
            "ui": {
                "file_content_align": "center",
                "file_metadata_editor_visible": True,
                "spatial_metadata_editor_visible": False,
                "spatial_region_label_attribute_id": ""
            }
        },
        "attribute": {
            "1": {
                "aname": "Activity",
                "anchor_id": "FILE1_Z2_XY0",
                "type": 1,
                "desc": "Activity",
                "options": {},
                "default_option_id": ""
            },
            "2": {
                "aname": "video",
                "anchor_id": "FILE1_Z1_XY1",
                "type": 3,
                "desc": "video Object",
                "options": {
                    "0": "board",
                    "1": "truck",
                    "2": "person"
                },
                "default_option_id": "0"
            },
            "3": {
                "aname": "img",
                "anchor_id": "FILE1_Z0_XY1",
                "type": 3,
                "desc": "image Object",
                "options": {
                    "0": "board",
                    "1": "truck",
                    "2": "person"
                },
                "default_option_id": "0"
            }
        },
        "file":{},
        "metadata":{},
        "view":{}
        
        
    }
    img_index = 0

    with open(list_name, "r", encoding="utf8") as fp_list_txt:

        for line in fp_list_txt.readlines():
            # get base infomation for read file
            temp = line.strip().split("/")
            filename_txt = temp[-1][0:-3] + "txt"  # xxx.txt
            filename_img = temp[-1]                 # xxx.jpg
            file_data_path = temp[-2]  # true_data
            line = line.strip()
            if platform.system() == 'Windows':
                line = os.path.join(file_data_path, filename_img)  # 获取到本地相对路径

            if not os.path.exists(line):
                continue

            line_img = line
            line_txt = line[0:-3] + "txt"

            # read image and save its size
            img_index += 1

            im = Image.open(line_img)  # 返回一个Image对象
            print(img_index, '  width：%d,height：%d' % (im.size[0], im.size[1]))
            now_img_width = im.size[0]
            now_img_height = im.size[1]

            # add vid_list
            pid_json_data['project']['vid_list'].append(str(img_index))

            # add view
            pid_json_data['view'][str(img_index)] = {
                "fid_list": [str(img_index)]
            }

            # add file
            pid_json_data["file"][str(img_index)] = {
                "fid": str(img_index),
                # "fname": os.path.join(url_path, item.replace('#', '%23')),# ?
                "fname": line.replace('#', '%23'),
                "type": 2,
                "loc": 2,
                "src": line.replace('#', '%23')
            }

            # uuid3
            uuid_mid = str(uuid.uuid3(uuid.NAMESPACE_DNS, line))[2:8]

            with open(line_txt, 'r') as fp_line_txt:
                file_data = fp_line_txt.readlines()
                if len(file_data) == 0:
                    # 添加负数据集
                    pid_json_data['metadata'][str(img_index) + '_' + uuid_mid] = {
                        "vid": str(img_index),
                        "flg": 0,
                        "z": [],
                        "xy": [
                            3,
                            678.225,
                            379.659,
                            202.101
                        ],
                        "av": {
                            "1": "_DEFAULT"
                        }
                    }
                else:
                    # 添加正数据集
                    for item in file_data:
                        uuid_mid = str(uuid.uuid3(
                            uuid.NAMESPACE_DNS, item))[2:8]

                        item_arr = item.split(' ')
                        print("item_arr: ", item_arr)

                        x = float(item_arr[1]) * now_img_width
                        y = float(item_arr[2]) * now_img_height

                        w = float(item_arr[3]) * now_img_width
                        h = float(item_arr[4]) * now_img_height

                        print('x: {}, y: {}, w: {}, h: {}'.format(x, y, w, h))

                        xmax = (w + (x + 1) * 2) / 2
                        xmin = xmax - w

                        ymax = ((y + 1) * 2 + h) / 2
                        ymin = ymax - h
                        if item_arr[0] == '0':
                            item_arr[0] = "1"
                        pid_json_data['metadata'][str(img_index) + '_' + uuid_mid] = {
                            "vid": str(img_index),
                            "flg": 0,
                            "z": [],
                            "xy": [
                                2,
                                xmin,
                                ymin,
                                w,
                                h
                            ],
                            "av": {
                                "1": "_DEFAULT",
                                "2": item_arr[0],
                                "3": item_arr[0]
                            }
                        }
    
    print(pid_json_data)
    json_filename = pid_name + ".json"
    print("json_filename=", json_filename)
    json_full_path = os.path.join(save_position, json_filename)
    print("json_file_path=", json_full_path)
    with open(json_full_path,"w+",encoding="utf8") as fp_json:
        fp_json.write(json.dumps(pid_json_data,indent=2))

read_list_file(list_file_path, json_file_path)
    

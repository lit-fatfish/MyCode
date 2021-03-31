# 通过获取图片的数据和yolo格式的txt文档，转换成pid文件


import os
import platform
from datetime import date
import json
import uuid
import time
from PIL import Image

img_path = r"/mnt/softdata/download/船舶/VOCdevkit/VOC2007/images"
txt_path = r"/mnt/softdata/download/船舶/VOCdevkit/VOC2007/labels"

pid_path = r"/home/anlly/train/flask/store"

new_img_path = r"/mnt/softdata/project_data/data_boat/20210313_boat"

record_json_name = "/mnt/auxnas/nas_project/frank/Code/json_name.txt"


img_list = os.listdir(img_path)

txt_list = os.listdir(txt_path)


print(len(img_list), img_list[0])


pid_name = str(uuid.uuid4())
print(pid_name)
# pid_name = "0000000"
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
                # "0": "board",
                # "1": "truck",
                # "2": "person"
                "0": "boat"
            },
            "default_option_id": "0"
        },
        "3": {
            "aname": "img",
            "anchor_id": "FILE1_Z0_XY1",
            "type": 3,
            "desc": "image Object",
            "options": {
                # "0": "board",
                # "1": "truck",
                # "2": "person"
                "0": "boat"
            },
            "default_option_id": "0"
        }
    },
    "file":{},
    "metadata":{},
    "view":{}
    
    
}
is_copy_img = True
img_index = 0
file_num = 0


for img in img_list:
    img_full_path = os.path.join(img_path, img)
    print(img_full_path)
    if not os.path.exists(img_full_path):
        continue
    
    txt_full_path = os.path.join(txt_path, img.split('.')[0] + '.txt')   
    print(txt_full_path)
    if not os.path.exists(txt_full_path):
        continue
    
    img_index += 1

    im = Image.open(img_full_path)  # 返回一个Image对象
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
    # 文件路径 
    fname = './ftp_video/user'
    if is_copy_img:
        new_img_full_path = os.path.join(new_img_path, img)
        os.system("cp {} {}".format(img_full_path, new_img_full_path))
        temp = new_img_full_path.split('/')
        print(temp)
        for url_file in temp[3:]:
            fname = os.path.join(fname,url_file)
        print(fname)
    else:
        pass
    pid_json_data["file"][str(img_index)] = {
        "fid": str(img_index),
        # "fname": os.path.join(url_path, item.replace('#', '%23')),# ?
        "fname": fname.replace('#', '%23'),
        "type": 2,
        "loc": 2,
        "src": fname.replace('#', '%23')
    }

    # uuid3
    uuid_mid = str(uuid.uuid3(uuid.NAMESPACE_DNS, img_full_path))[2:8]

    with open(txt_full_path, 'r') as fp_line_txt:
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
                # print("item_arr: ", item_arr)

                x = float(item_arr[1]) * now_img_width
                y = float(item_arr[2]) * now_img_height

                w = float(item_arr[3]) * now_img_width
                h = float(item_arr[4]) * now_img_height

                # print('x: {}, y: {}, w: {}, h: {}'.format(x, y, w, h))

                xmax = (w + (x + 1) * 2) / 2
                xmin = xmax - w

                ymax = ((y + 1) * 2 + h) / 2
                ymin = ymax - h
                # if item_arr[0] == '0':
                #     item_arr[0] = "1"
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
    # end with open txt
    if img_index == 1000:
        file_num += 1
        pid_json_data['project']['pid'] = pid_name + "-" + str(file_num)
        json_filename = pid_name + "_" + str(file_num) + ".json"
        with open(record_json_name, "a+",encoding="utf8") as fp_json_name:
            fp_json_name.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\t" + json_filename + "\n")
        json_full_path = os.path.join(pid_path, json_filename)
        with open(json_full_path,"w+",encoding="utf8") as fp_json:
            fp_json.write(json.dumps(pid_json_data,indent=2))

        img_index = 0
        pid_json_data['view'] = {}
        pid_json_data['file'] = {}
        pid_json_data['metadata'] = {}
        pid_json_data['project']['vid_list'] = []
    
if file_num > 0:
    file_num += 1
    pid_json_data['project']['pid'] = pid_name + "-" + str(file_num)
    json_filename = pid_name + "_" + str(file_num) + ".json"
else:
    json_filename = pid_name + ".json"

print("file_num=",file_num)

# print("pid_json_data",pid_json_data)
print("json_filename=", json_filename)

print("record_json_name=",record_json_name)
with open(record_json_name, "a+",encoding="utf8") as fp_json_name:
    fp_json_name.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\t" + json_filename + "\n")

json_full_path = os.path.join(pid_path, json_filename)
print("json_full_path=", json_full_path)
with open(json_full_path,"w+",encoding="utf8") as fp_json:
    fp_json.write(json.dumps(pid_json_data,indent=2))














# 想法，读取pid文件，然后根据标签删除框
import os, json


src_pid_path = ""

dst_pid_path = ""

def read_jsonfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

            return json_data
    else:
        # 文件名不存在，写入日志
        print("文件不存在")
        return False

def write_jsonfile(filename, data):
    with open(filename, 'w', encoding='utf8')as f:
        json.dump(data, f, indent=2)

pid_dic = read_jsonfile(src_pid_path)

for item in pid_dic["metadata"]:
    tag = pid_dic["metadata"][item]['av']['2']
    if tag != "1":
        del pid_dic["metadata"][item]



write_jsonfile(dst_pid_path, pid_dic)

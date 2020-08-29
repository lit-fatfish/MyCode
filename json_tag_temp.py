# 修改pid.json中的标签格式
import json,os

def read_jsonfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

            return json_data
    else:
        # 文件名不存在，写入日志
        print("文件不存在")
        return False

json_path = "/home/anlly/machine_learning/docker/flask/store/2ec336fc-e789-11ea-8d39-536327161d36.json"

dic_json = read_jsonfile(json_path)

for item in dic_json["metadata"]:
    # print(dic_json["metadata"][item])
    if dic_json["metadata"][item]["av"]["2"] == "0":
        dic_json["metadata"][item]["av"]["2"] = "1"
        # print(dic_json["metadata"][item]["av"]["2"])
    if dic_json["metadata"][item]["av"]["3"] == "0":
        dic_json["metadata"][item]["av"]["3"] = "1"
        # print(dic_json["metadata"][item]["av"]["3"])


with open(json_path, 'w') as f:
    f.write(json.dumps(dic_json,indent=2))
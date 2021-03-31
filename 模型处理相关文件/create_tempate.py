# 根据输入的参数，生成一个新的配置文件
import os,json


bak_template_path = "/mnt/auxnas/nas_project/frank/Code/template" # 自己备份的template文件

new_template_path = "/rtx_train_data/boat/template" # 新生成的template路径

# 参数

# start
def read_txtfile(filename):
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf8") as fp:
            lines = fp.readlines()
            return lines


def write_txtfile(filename, data):
    with open(filename, "w", encoding="utf8") as fp:
        for item in data:
            fp.write(item)


def write_voc_name(path, class_name):
    # 读备份里面的文件
    # read_txtfile()

    # 写到新的路径下面
    with open(path, "w+", encoding="utf8") as fp:
        for index,item in enumerate(class_name):
            if index == len(class_name) - 1:
                fp.write(item)
            else:
                fp.write(item + '\n')

def write_voc_data(bak_template_path, path, class_num):
    bak_voc_data_path = os.path.join(bak_template_path, "voc.data")
    data = read_txtfile(bak_voc_data_path)
    data[0] = "classes = " + str(class_num) + '\n'
    print(data)

    write_txtfile(path, data)

def write_voc_yaml(src_path, dst_path):
    cp_cmd = "cp " + src_path + " " + dst_path
    os.system(cp_cmd)
      
def write_voc_cfg(bak_template_path, path,classes,filter_num,max_step,step):
    filename = os.path.split(path)[-1]
    cfg_path = os.path.join(bak_template_path, filename)
    cfg_lines = read_txtfile(cfg_path)

    for index,item in enumerate(cfg_lines):
        # print(item)
        if  "max_batches" in item :
            print(item)
            cfg_lines[index] = "max_batches = " + str(max_step) + "\n"
            cfg_lines[index + 2] = "steps=" + str(step) + "\n"
        elif "classes" in item:
            print(item)
            cfg_lines[index] = "classes=" + str(classes) + "\n"
        elif "yolo" in item:
            filter_index = index - 3
            print(cfg_lines[filter_index])
            cfg_lines[filter_index] = "filters=" + str(filter_num) + "\n"


    write_txtfile(path, cfg_lines)
    # for item in cfg_lines:
    #     print(item)
    # print(cfg_lines)
## 确定参数
# classes = 2

# class_name = ["smoke","dust"]

# filter_num = 3 * (classes + 5)

# max_batches = "25000"
# steps = "18000,23000"

# print(classes)
# print(class_name)
# print(filter_num)

data = {
    "bak_template_path":"/mnt/auxnas/nas_project/frank/Code/template",
    "new_template_path" : "/rtx_train_data/boat/template" ,
    "classes" : 2,
    "class_name": ["boat","smoke"],
    "max_batches":"25000",
    "steps":"18000,23000"
}


def add_template(data):
    # 获取参数
    bak_template_path = data["bak_template_path"]
    new_template_path = data["new_template_path"]
    classes = data["classes"]
    filter_num = 3 * (classes + 5)
    class_name = data["class_name"]
    max_batches = data["max_batches"]
    steps = data["steps"]
    print(data)

    if new_template_path == "":
        return False
    new_template_path = "/mnt" + new_template_path
    new_template_path = os.path.join(new_template_path, "template")
    print(new_template_path)
    if not os.path.exists(new_template_path):
        os.mkdir(new_template_path)

    

    ######## voc.names
    voc_name_file = os.path.join(new_template_path, "voc.names")
    write_voc_name(voc_name_file, class_name)

    ######## voc.data
    voc_data_file = os.path.join(new_template_path, "voc.data")
    write_voc_data(bak_template_path, voc_data_file, classes)

    ####### voc.yaml
    voc_yaml_src_path = os.path.join(bak_template_path, "voc.yaml")
    voc_yaml_dst_path = os.path.join(new_template_path, "voc.yaml")

    write_voc_yaml(voc_yaml_src_path, voc_yaml_dst_path)

    ####### voc.cfg
    voc_cfg_path = os.path.join(new_template_path, "voc.cfg")
    write_voc_cfg(bak_template_path, voc_cfg_path, classes, filter_num,max_batches, steps)

    ####### voc_test.cfg
    voc_test_cfg_path = os.path.join(new_template_path, "voc_test.cfg")
    write_voc_cfg(bak_template_path, voc_test_cfg_path, classes, filter_num,max_batches, steps)

if __name__ == "__main__":
    add_template(data)



## 一一写入






    
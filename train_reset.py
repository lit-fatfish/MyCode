# 用于将训练失败的模型删除，并回退到上一个版本
"""
pid文件名
删除train.txt、list.txt、test.txt

"""

# 思考实现方式
# 读取所有的train_xxx.txt文件,
# 读取每一个文件，并写入到train.txt中
# 并将

# 实现步骤
# 1、复制train.txt / list.txt / test.txt文件
# 2、读取文件 train_xxx.txt
# 3、将文件写入到train.txt中，所有
# 4、

import os

model_path = "/home/anlly/workspace/rtx_train_data/building_site/hat/20200815_hat"

remove_file = "train_fa74ad78-e124-11ea-ac42-f753bb0383f1_1111.txt"

remove_full_path = os.path.join(model_path,remove_file)
# print(remove_full_path)
# if not os.path.exists(remove_file):
#     print("remove file not found")
#     exit(0)
new_train_txt = os.path.join(model_path, "new_train.txt")
with open(new_train_txt, "w+"):
    pass
new_txts = []

file_list = os.listdir(model_path)
for item in file_list:
    if item == remove_file:
        pass
        # 根据路径删除图片
        full_path = os.path.join(model_path, item)
        print(item)
        with open(full_path, 'r') as fp:
            for line in fp.readlines():
                # temp = line.strip().split("/")
                # print(temp)
                # print(line[0:11] +"/workspace" + line[66:])
                # new_line = os.path.join(temp[0],temp[1],"workspace",)
                print(line)
                line = line.strip()
                line_txt = line[0:-3] + "txt"
                line_jpg = line
                if os.path.exists(line_txt):
                    os.remove(line_txt)
                    print("txt file exists\n")

                if os.path.exists(line_jpg):
                    os.remove(line_jpg)
                    print("image file exists\n")
    # 文件是train_开头的
    elif item[0:6] == "train_":
        full_path = os.path.join(model_path, item)
        print(item)
        with open(full_path, 'r') as fp:
            txt_lines = fp.readlines()
            for i in range(len(txt_lines)):
                temp_path = txt_lines[i][0:11] +"/workspace" + txt_lines[i][66:]
                # print(temp_path)
                os.path.exists
                if not os.path.exists(temp_path.strip()):
                    print("不存在")
                    continue
                
                new_txts.append(temp_path)


        
# write in train.txt
print('len:', len(new_txts))
new_txts_bak = list(set(new_txts))

print('len:', len(new_txts_bak))

with open(new_train_txt, "a+", encoding="utf8") as fp_new:
    for line_temp in new_txts_bak:
        fp_new.write(line_temp)
            
# print(file_list)

print("hello world")
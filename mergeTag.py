# 目标
# 第一步，实现标签的修改


# 步骤
# 读取list文件，根据文件地址去读取文件和图片，并读取图片的大小和修改txt文件中的序号（标签）
import os
import platform
from datetime import date

if platform.system() == 'Windows':
    list_file_path = "new_list.txt"
    new_file_path = "."
elif platform.system() == 'Linux':
    list_file_path = "/home/anlly/workspace/rtx_train_data/truck/truck_20200509_new/list.txt"
    new_file_path = "/home/anlly/machine_learning/tag_test"


def read_list_file(filename, src, dst, new_path):
    if not os.path.exists(filename):
        return False
    # create a new folder
    new_folder_name = "frank_" + str(date.today())
    new_file_path = os.path.join(new_path, new_folder_name)
    print("new_file_path=",new_file_path)
    if not os.path.exists(new_file_path):
        os.mkdir(new_file_path)

    with open(filename, 'r', encoding='utf8')as fp:
        # open list.txt file
        for line in fp.readlines():
            # in Linux path = /home/anlly/workspace/rtx_train_data/truck/truck_20200509_new/true_data/22101c9e-abf3-4893-b200-c3b0c9a8466b.mp4#0.448.jpg
            # in Window path = true_data/22101c9e-abf3-4893-b200-c3b0c9a8466b.mp4#0.448.jpg
            temp = line.strip().split("/")
            filename_txt = temp[-1][0:-3] + "txt"  # xxx.txt
            filename_img = temp[-1]                 # xxx.jpg
            file_data_path = temp[-2]  # true_data
            # file_path = temp[-2]  # true_data
            line = line.strip()
            if platform.system() == 'Windows':
                line = os.path.join(file_data_path, filename_img)  # 获取到本地相对路径

            if not os.path.exists(line):
                continue
            line_img = line
            line_txt = line[0:-3] + "txt"
            print(line_txt)
            # create true_data folder
            new_data_path = os.path.join(new_file_path, file_data_path)
            if not os.path.exists(new_data_path):
                os.mkdir(new_data_path)

            with open(line_txt, "r+", encoding="utf8") as fp_txt:
                fp_txt.seek(0)
                line_txts = fp_txt.readlines()
                print(line_txts)
                print("line_txts_length",len(line_txts))
                for i in range(len(line_txts)):
                    if line_txts[i][0:1] == src:
                        line_txts[i] = dst + line_txts[i][1:]
                # write txt data to another folder
                new_txt_path = os.path.join(new_data_path, filename_txt)

                print("new_data_path=",new_data_path)

                with open(new_txt_path, "w+", encoding="utf8") as fp_new:
                    for line_temp in line_txts:
                        fp_new.write(line_temp)

            # copy jpg file to another folder
            new_img_path = os.path.join(new_data_path, filename_img)

            f_src = open(line_img, 'rb')
            content = f_src.read()
            f_copy = open(new_img_path, 'wb')
            f_copy.write(content)
            f_src.close()
            f_copy.close()


read_list_file(list_file_path, "0", "1", new_file_path)

# import re
#
#
# line="this hdr-biz model server"
# pattern="hdr-biz11"
# m = re.search(pattern, line)
# print(m)

# 写一个简单的函数，读取文件名，并且获取一个匹配图片的列表
# list = os.listdir("true_data")
#
# for filename in list:
#     with open("list copy.txt","r",encoding="utf8") as fp:
#         for line in fp.readlines():
#             # 假如整行匹配到filename，则写入到文件中
#             result = re.search(filename, line)
#             if result:
#                 with open("new_list.txt","a+",encoding="utf8") as fp:
#                     fp.writelines(line)

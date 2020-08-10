# 目标
# 第一步，实现标签的修改


# 步骤
# 读取list文件，根据文件地址去读取文件和图片，并读取图片的大小和修改txt文件中的序号（标签）
import os
import platform
from datetime import date


# list_file_path = "/home/anlly/workspace/rtx_train_data/truck/truck_20200509_new/train.txt"  # 大车
# list_file_path = "/home/anlly/workspace/rtx_train_data/darkness/darkness_smoke_20200723/train.txt" # 黑烟
list_file_path = "/home/anlly/workspace/rtx_train_data/hat/hat_20200522/train.txt" # 人与安全帽
# new_file_path = "/home/anlly/machine_learning/tag_test"
new_file_path = "/home/anlly/machine_learning/docker/main-nginx/html/ftp_video/user/nas_project/frank"

data_type = "_person"


# 存放的位置
base_local_path = '/home/anlly/machine_learning/docker/main-nginx/html/ftp_video/user/'

def read_list_file(filename, src, dst, new_path):
    if not os.path.exists(filename):
        print("files not found")
        return False
    # create a new folder
    new_folder_name = ''.join(str(date.today()).strip().split('-')) + data_type
    new_train_path = os.path.join(new_path, new_folder_name)
    new_file_path = os.path.join(new_path, new_folder_name,"true_data")  #  /xx/xxx/xxx/true_data
    print("new_file_path=",new_file_path)
    if not os.path.exists(new_file_path):
        os.makedirs(new_file_path)

    index = 0
    train_txt = []

    with open(filename, 'r', encoding='utf8')as fp:
        # open list.txt file
        for line in fp.readlines():
            # if index == 10:
            #     break
            line = line.strip() 
            temp = line.strip().split("/")
            filename_txt = temp[-1][0:-3] + "txt"  # xxx.txt
            filename_img = temp[-1]                 # xxx.jpg

            if not os.path.exists(line):
                continue
            # get full path of img and txt
            line_img = line
            line_txt = line[0:-3] + "txt"
            print("line_txt=", line_txt)
            

            with open(line_txt, "r+", encoding="utf8") as fp_txt:
                fp_txt.seek(0)
                line_txts = fp_txt.readlines()
                if not line_txts:
                    continue
                # print(line_txts)
                print("line_txts_length",len(line_txts))
                # if need update tags
                # for i in range(len(line_txts)):
                #     if line_txts[i][0:1] == src:
                #         line_txts[i] = dst + line_txts[i][1:]
                
                # pick hat from person and hat    
                temp_lines = []
                for i in range(len(line_txts)):
                    if line_txts[i][0:1] == '1':
                        line_txts[i] = '2' + line_txts[i][1:]
                        temp_lines.append(line_txts[i])
                if not temp_lines:
                    continue
                
                line_txts = temp_lines 
                print(line_txts)
                # write txt data to another folder
                new_txt_path = os.path.join(new_file_path, filename_txt)
                # print("new_txt_path=",new_txt_path)

                with open(new_txt_path, "w+", encoding="utf8") as fp_new:
                    for line_temp in line_txts:
                        fp_new.write(line_temp)

            # copy jpg file to another folder
            new_img_path = os.path.join(new_file_path, filename_img)
            print("new_img_path=", new_img_path)
            f_src = open(line_img, 'rb')
            content = f_src.read()
            f_copy = open(new_img_path, 'wb')
            f_copy.write(content)
            f_src.close()
            f_copy.close()
            train_txt.append(new_img_path + "\n")
            index += 1
            print("index=",index)
    
    new_train_full_path = os.path.join(new_train_path, "train.txt")
    print("sum = ",index)
    print("new_train_full_path=",new_train_full_path)
    # print("tain_txt=",train_txt)
    with open(new_train_full_path, "w+", encoding="utf8") as fp_train:
        for train in train_txt:
            fp_train.write(train)


# read_list_file(list_file_path, "0", "1", new_file_path)
read_list_file(list_file_path, "0", "0", new_file_path)





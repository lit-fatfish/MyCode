# 在已经训练好的模型中选择其中一个标签，生成训练数据
import os 

src_path = "/mnt/rtx_train_data/vehicle/vehicle_board/vehicle_board_20210320/true_data"

dst_path = "/mnt/rtx_train_data/vehicle/person/person_20210408/true_data"

train_path = "/mnt/rtx_train_data/vehicle/person/person_20210408"


listdirs = os.listdir(src_path)
train_txt = []

for index, file_name in enumerate(listdirs):
    print(index)
    if not file_name.endswith('.txt'):
        continue
    img_full_path = os.path.join(src_path, os.path.splitext(file_name)[0] + '.jpg')
    txt_full_path = os.path.join(src_path, file_name)
    if not os.path.exists(img_full_path):
        continue

    # 正式处理
    with open(txt_full_path, 'r', ) as fp_txt: 
        lines = fp_txt.readlines()
        is_copy_img = 0
        line_txts = []
        for index1,item1 in enumerate(lines):
            tag = item1.split(' ')[0]
            if tag == "1":    # 人
                is_copy_img = 1
                line_txts.append("0" + item1[1:])

        if is_copy_img:
            # 拷贝图片
            # 写入txt文件
            temp_txt = os.path.join("/home/anlly/workspace/rtx_train_data", img_full_path.split("rtx_train_data")[1][1:])
            train_txt.append(temp_txt+"\n")
            img_dst_path = os.path.join(dst_path, os.path.splitext(file_name)[0] + '.jpg')
            txt_dst_path =  os.path.join(dst_path, file_name)
            os.system("cp {} {}".format(img_full_path, img_dst_path))
            with open(txt_dst_path, "w+", encoding="utf8") as fp_new:
                for line_temp in line_txts:
                    fp_new.write(line_temp)

with open(os.path.join(train_path, "train.txt"), "w+", encoding="utf8") as fp_new:
    for line_temp in train_txt:
        fp_new.write(line_temp)

with open(os.path.join(train_path, "list.txt"), "w+", encoding="utf8") as fp_new:
    for line_temp in train_txt:
        fp_new.write(line_temp)

with open(os.path.join(train_path, "test.txt"), "w+", encoding="utf8") as fp_new:
    for line_temp in train_txt:
        fp_new.write(line_temp)
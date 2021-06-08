# 读取之前的文件夹，然后将图片合并后放在新的目录
import os, cv2
import numpy as np

src_path = r"/mnt/softdata/project_data/data_truck/20210410_truck/东湾大道-100_unzip"


dst_path = r"/mnt/softdata/project_data/data_truck/20210410_truck/data_set"


listdir = os.listdir(src_path)

# print(listdir)
# 初步定为两层目录


img_index = 0

for index, item in enumerate(listdir):
    
    # if img_index >= 10:
    #     exit(0)

    floder_path = os.path.join(src_path, item)
    if not os.path.isfile(floder_path):
        print("is floder")
        # 这个好像不需要，直接找到对应的文件名即可
        # second_list_dir = os.listdir(floder_path)
        # for index1, item1 in enumerate(second_list_dir):
        #     file_path = os.path.join(floder_path, item1)
        #     print(file_path)
        head_path = os.path.join(floder_path, "head.jpg")
        if not os.path.exists(head_path):
            continue
        for i in range(1,4):
            print(i)
            tail_path = os.path.join(floder_path, 'tail' + str(i) +".jpg")
            if not os.path.exists(tail_path):
                continue
            print(tail_path)
            print(head_path)
            # 存在，和成图片
            head_img = cv2.imread(head_path)
            tail_img = cv2.imread(tail_path)
            # print(len(head_img)) 
            # print(len(tail_img))
            new_img = np.ndarray((256,512,3))
            head_img = cv2.resize(head_img, (256, 256))
            tail_img = cv2.resize(tail_img, (256, 256))
            new_img[:,0:256] = head_img
            new_img[:,256:512] = tail_img
            img_index += 1
            print("img_index", img_index)

            
            img_name = item + "_car{}.jpg".format(str(i))
            
            if img_index % 10 == 0:
                # 验证集
                img_path = os.path.join(dst_path, "val")
            else:
                # 训练集
                img_path = os.path.join(dst_path, "train")

                if (img_index % 10 == 8) or (img_index % 10 == 9):
                    # 测试集
                    test_path = os.path.join(dst_path, "test")
                    cv2.imwrite(os.path.join(test_path, img_name), new_img)
            cv2.imwrite(os.path.join(img_path, img_name), new_img)
    else:
        # print("is file")
        pass



import os
import cv2
from PIL import Image
import time

# 以文件的形式读取图片，剪切并保存

file_path = "/home/anlly/workspace/rtx_train_data/building_site/hat/20200815_hat"

hat_path = "temp/train_bab34e4c-e43f-11ea-8d39-536327161d36/hat"

person_path = "temp/train_bab34e4c-e43f-11ea-8d39-536327161d36/person"

txt_list = os.listdir(file_path)

print(len(txt_list))

count_txt = 0
count_jpg = 0

index = 0
for item in txt_list:
    print(item)
    # if item[0:6] == "train_":   #扫描全部
    if item == "train_bab34e4c-e43f-11ea-8d39-536327161d36.txt":  #只执行单个
        with open(item, "r") as fp_train_txt:
            for train_line in fp_train_txt.readlines():
                index += 1
                train_line = train_line.strip()
                print(index)
                if index >= 5:
                    pass
                    # exit(0) 
                train_line_jpg = train_line.strip()
                if not os.path.exists(train_line):
                    continue
                train_line_txt = train_line_jpg[0:-3] + 'txt'
                with open(train_line_txt, "r") as fp_txt:
                    for txt_line in fp_txt.readlines():

                        im = Image.open(train_line_jpg)  # 返回一个Image对象
                        print('  width：%d,height：%d' % (im.size[0], im.size[1]))
                        now_img_width = im.size[0]
                        now_img_height = im.size[1]

                        item_arr = txt_line.split(' ')
                        # print("item_arr: ", item_arr)
                        tag = item_arr[0]

                        x = float(item_arr[1]) * now_img_width
                        y = float(item_arr[2]) * now_img_height

                        w = float(item_arr[3]) * now_img_width
                        h = float(item_arr[4]) * now_img_height

                        xmax = (w + (x + 1) * 2) / 2
                        xmin = xmax - w

                        ymax = ((y + 1) * 2 + h) / 2
                        ymin = ymax - h

                        print(x, y, w, h)
                        print(tag)
                        img = cv2.imread(train_line_jpg)
                        copy_img = img[int(ymin):int(ymin+h), int(xmin):int(xmin+w)]

                        temp = train_line_jpg.split("/")

                        img_filename = item[0:-4] + "_" + temp[-1][0:-4] + "_" + \
                            str(int(time.time()*10000)) + ".jpg"
                        if tag == "0":
                            new_path = os.path.join(hat_path, img_filename)

                        elif tag == "1":
                            new_path = os.path.join(person_path, img_filename)

                        print(new_path)

                        cv2.imwrite(new_path, copy_img)





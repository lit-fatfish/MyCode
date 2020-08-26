import os
import cv2
from PIL import Image
import time
# 获取true_data中的数据，并且剪切图片保存


file_path = "true_data"

txt_list = os.listdir(file_path)

print(len(txt_list))

count_txt = 0
count_jpg = 0

index = 0
for item in txt_list:
    index +=1 
    print("index=", index)
    if index >= 10:
        pass
        # break
    if item.endswith(".txt"):
        count_txt += 1
        
        # print(item)
        # read txt file
        txt_path = os.path.join(file_path, item)
        with open(txt_path, "r") as fp:
            for line in fp.readlines():
                img_path = txt_path[:-3] + "jpg"
                print(img_path)

                im = Image.open(img_path)  # 返回一个Image对象
                print('  width：%d,height：%d' % (im.size[0], im.size[1]))
                now_img_width = im.size[0]
                now_img_height = im.size[1]

                item_arr = line.split(' ')
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

                print(x,y,w,h)
                print(tag)
                img = cv2.imread(img_path)
                copy_img = img[int(ymin):int(ymin+h), int(xmin):int(xmin+w)]

                img_filename = item[0:-4] + "_" + str(int(time.time()*10000)) + ".jpg"
                

                if tag == "0":
                    new_path = os.path.join("temp/hat", img_filename)


                elif tag == "1":
                    new_path = os.path.join("temp/person", img_filename)

                print(new_path)

                cv2.imwrite(new_path, copy_img)

                

    # elif item.endswith(".jpg"):
    #     count_jpg +=1

print("txt", count_txt)
print("jpg", count_jpg)
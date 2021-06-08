# 根据图片和txt文档，测试数据是否正常

import os, cv2, json



true_data_path = "D:\Code\MyCode\model_test\img"

dst_data_path = r"D:\Code\MyCode\model_test\new_img"

listdirs = os.listdir(true_data_path)


def read_jsonfile(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf8')as fp:
            json_data = json.load(fp)

            return json_data
    else:
        # 文件名不存在，写入日志
        print("文件不存在")
        return {}

for index, item in enumerate(listdirs):
    if item.endswith('jpg'):
        txt_name = os.path.splitext(item)[0] + ".txt"
        print(item)
        print(txt_name)
        img_full_path = os.path.join(true_data_path, item)
        txt_full_path = os.path.join(true_data_path, txt_name)
        if not os.path.exists(img_full_path):
            continue
        if not os.path.exists(txt_full_path):
            continue

        # 根据txt文档，取出框的数据，画框，保存图片
        # txt_data = read_jsonfile(txt_full_path)
        # print(txt_data)
        with open(txt_full_path, 'r', encoding='utf8') as fp:
            lines = fp.readlines()

            print(lines)
            img = cv2.imread(img_full_path)
            now_img_height, now_img_width, _ = img.shape
            for line in lines:
                # print(line, type(line[1]))
                # line = json.load(line)
                item_arr = line.split(' ')
                x = float(item_arr[1]) * now_img_width
                y = float(item_arr[2]) * now_img_height

                w = float(item_arr[3]) * now_img_width
                h = float(item_arr[4]) * now_img_height

                xmax = int((w + (x + 1) * 2) / 2)
                xmin = int(xmax - w)

                ymax = int(((y + 1) * 2 + h) / 2)
                ymin = int(ymax - h)
                pt1 = (xmin, ymin)
                pt2 = (xmax, ymax)
                color = (0, 0, 255) 
                cv2.rectangle(img, pt1, pt2, color, 1)
            
            dst_full_path = os.path.join(dst_data_path, item)
            cv2.imwrite(dst_full_path, img)







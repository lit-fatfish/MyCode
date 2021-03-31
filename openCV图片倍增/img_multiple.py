import cv2, os


src_path = "/mnt/softdata/frank/model_data/img/20210128/board_RB_4"


dis_path = "/mnt/softdata/frank/model_data/img/20210129/"



dirlists = os.listdir(src_path)

temp = src_path.strip().split('/')
floder = temp[-1]

dis_path = os.path.join(dis_path, floder)
if not os.path.exists(dis_path):
    os.makedirs(dis_path)

for index, file_name in enumerate(dirlists):
    print(file_name)
    src_full_path = os.path.join(src_path, file_name)
    if not src_full_path.endswith('.jpg'):
        continue
    img = cv2.imread(src_full_path)
    print(len(img))
    if len(img) == 0:
        continue
    cv2.imwrite(os.path.join(dis_path ,file_name), img)
    #1. 左右镜像，水平翻转
    new_img = cv2.flip(img, 1)
    new_file_name = file_name.split('.')[0] + "_left_rigth" +  ".jpg"
    # print(new_file_name)
    cv2.imwrite(os.path.join(dis_path ,new_file_name), new_img)

    #2. 上下镜像，垂直翻转
    new_img = cv2.flip(img, 0)
    new_file_name = file_name.split('.')[0] + "_up_down" +  ".jpg"
    cv2.imwrite(os.path.join(dis_path, new_file_name), new_img)


    #3. 上下左右镜像，垂直翻转  + 水平翻转
    new_img = cv2.flip(img, -1)
    new_file_name = file_name.split('.')[0] + "_around" +  ".jpg"
    cv2.imwrite(os.path.join(dis_path, new_file_name), new_img)

    # 4.转置
    trans_img = cv2.transpose(img)
    new_file_name = file_name.split('.')[0] + "_transpose" +  ".jpg"
    cv2.imwrite(os.path.join(dis_path, new_file_name), trans_img)

    # 5.顺时针旋转90度
    clockwise_img = cv2.flip(trans_img, 1)
    new_file_name = file_name.split('.')[0] + "_clockwise" +  ".jpg"
    cv2.imwrite(os.path.join(dis_path, new_file_name), clockwise_img)

    # 6.逆时针旋转90度
    anti_clockwise_img = cv2.flip(trans_img, 0)
    new_file_name = file_name.split('.')[0] + "anti_clockwise" +  ".jpg"
    cv2.imwrite(os.path.join(dis_path, new_file_name), anti_clockwise_img)
    


    # break






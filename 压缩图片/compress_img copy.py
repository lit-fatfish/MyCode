import os, sys, cv2, time, json
import platform
import exifread
import zipfile
from PIL import Image


def convert_gps(coord_arr):
    arr = str(coord_arr).replace('[', '').replace(']', '').split(', ')
    d = float(arr[0])
    m = float(arr[1])
    s = float(arr[2].split('/')[0]) / float(arr[2].split('/')[1])

    gps = d+float(m/60)+float(s/3600)
    # print(round(gps, 10))
    return round(gps, 10)

def resize_image(infile, outfile='', x_s=1920):
    """修改图片尺寸
    :param infile: 图片源文件
    :param outfile: 重设尺寸文件保存地址
    :param x_s: 设置的宽度
    :return:
    """
    im = Image.open(infile)
    x, y = im.size
    y_s = int(y * x_s / x)
    out = im.resize((x_s, y_s), Image.ANTIALIAS)
    
    out.save(outfile)

def zipDir(dirpath,outFullName):
    """
    压缩指定文件夹
    :param dirpath: 目标文件夹路径
    :param outFullName: 压缩文件保存路径+xxxx.zip
    :return: 无
    """
    zip = zipfile.ZipFile(outFullName,"w",zipfile.ZIP_DEFLATED)
    for path,dirnames,filenames in os.walk(dirpath):
        # 去掉目标跟路径，只对目标文件夹下边的文件及文件夹进行压缩
        fpath = path.replace(dirpath,'')

        for filename in filenames:
            zip.write(os.path.join(path,filename),os.path.join(fpath,filename))
    zip.close()


def loadzip(dirpsth, outFullName):
## 解压
    filezip = zipfile.ZipFile(dirpsth,"r")
    # 遍历压缩包里的文件名
    for i in filezip.namelist():
        print(i)
        # extract方法进行解压，参数path为解压后的路径
        filezip.extract(i,path=outFullName)
    filezip.close()  



src_path = "img"

dst_path = 'new_img'

files = os.listdir(src_path)
jsonData = {}
for filename in files:
    dataInfo = {}

    temp = os.path.splitext(filename)
    # print(temp)
    if temp[1] not in ['.JPG']:
        continue
    src_full_path = os.path.join(src_path,filename)
    dst_full_path = os.path.join(dst_path,filename)
    img=exifread.process_file(open(src_full_path,'rb'))
    
    if temp[0][-1] == 'Z':
        # 需要压缩
        print(filename)
        resize_image(src_full_path, dst_full_path)
    else:
        # 不需要压缩，直接复制即可
        command = "copy {} {}".format(src_full_path, dst_full_path)
        os.system(command)

    if img['GPS GPSLongitude']:
        lng = convert_gps(img['GPS GPSLongitude'])
        lat = convert_gps(img['GPS GPSLatitude'])
        dataTime = str(img['Image DateTime'])
        data_sj = time.strptime(dataTime,"%Y-%m-%d %H:%M:%S")
        print(data_sj)
        time_int = int(time.mktime(data_sj))
        print('time',time_int)
        dataInfo['lng'] = lng
        dataInfo['lat'] = lat
        dataInfo['time'] = time_int
        jsonData[temp[0]] = dataInfo

print("jsonData", jsonData)
with open(os.path.join(dst_path, 'data.json'),'w',encoding='utf-8') as f:
    json.dump(jsonData, f, indent=2, ensure_ascii=False)


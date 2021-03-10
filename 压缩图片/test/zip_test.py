import zipfile, os


# zfile = zipfile.ZipFile('img.zip','r')
# print("namelist", zfile.namelist())
# for filename in zfile.namelist():
#     full_path = os.path.join(os.getcwd(), filename)
#     print(filename, full_path)
#     if os.path.isfile(full_path):    
#         data = zfile.read(full_path)
#         file = open(filename,'w+b')
#         file.write(data)
#         file.close()
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

# ## 解压
# filezip = zipfile.ZipFile("img.zip","r")
# # 遍历压缩包里的文件名
# for i in filezip.namelist():
#     print(i)
#     # extract方法进行解压，参数path为解压后的路径
#     filezip.extract(i,path=".")
# filezip.close()

dir_path = "DJI_202101061034_008_（8区-1）"

# zipDir(dir_path, dir_path + '.zip')

loadzip(dir_path + '.zip', '.')


# lists = os.listdir("new_img")
import os, sys, cv2, time, json
import platform
import exifread
import zipfile
from PIL import Image



def convert_gps(coord_arr):
    arr = str(coord_arr).replace('[', '').replace(']', '').split(', ')
    d = float(arr[0])
    m = float(arr[1])
    s_arr = arr[2].split('/')
    if len(s_arr)>1:
        s = (float(s_arr[0]) / float(s_arr[1]))
    else:
        s = float(s_arr[0])

    gps = d+float(m/60)+float(s/3600)
    # print(round(gps, 10))
    return round(gps, 10)

filename = "DJI_20210118161834_0326_Z.JPG"
filename = "DJI_20210118163430_0531_Z.JPG"

# img=exifread.process_file(open('DJI_20210118163430_0531_Z.JPG','rb'))
img=exifread.process_file(open(filename,'rb'))



jsonData = {}
dataInfo = {}

if img['GPS GPSLongitude']:
    # print(img)
    print(img['GPS GPSLongitude'])
    print(img['GPS GPSLatitude'])
    lng = convert_gps(img['GPS GPSLongitude'])
    lat = convert_gps(img['GPS GPSLatitude'])
    dataTime = str(img['Image DateTime'])
    data_sj = time.strptime(dataTime,"%Y-%m-%d %H:%M:%S")
    time_int = int(time.mktime(data_sj))
    dataInfo['lng'] = lng
    dataInfo['lat'] = lat
    dataInfo['time'] = time_int
    jsonData[filename] = dataInfo

print("jsonData", jsonData)


import cv2, time



# def check_camera(rtsp):
#     try:
#         cap = cv2.VideoCapture(rtsp)
#         ret, frame = cap.read()
#     except:
#  	    ret = False
#     return True if ret else False


### 能打开基本就几秒搞定了
def check_camera(rtsp):
    cap = cv2.VideoCapture(rtsp)
    ret, frame = cap.read()
    print(ret, frame)
    return True if ret else False

start_time = time.time()

print(check_camera("rtsp://192.168.31.52:554/source_2"))

end_time = time.time()

print("using time", end_time - start_time)
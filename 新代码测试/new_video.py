import cv2



cap = cv2.VideoCapture("./temp.mp4")


fps = int(cap.get(cv2.CAP_PROP_FPS))
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print(fps, width, height)


codec = cv2.VideoWriter_fourcc(*"mp4v")



new_cap = cv2.VideoWriter("new_test.mp4", codec, fps, (width, height))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret:
        new_cap.write(frame)
    else:
        new_cap.release()
        break




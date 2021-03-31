import cv2



cap = cv2.VideoCapture(r"D:\Code\MyCode\temp.mp4")

fps = int(cap.get(cv2.CAP_PROP_FPS))

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

size = (width, height)
print(fps, width, height)


codec = cv2.VideoWriter_fourcc(*"mp4v")

# size = (720, 1080)
# fps = 25

print(size)
new_cap = cv2.VideoWriter('test.mp4', codec, fps, size)

print(new_cap.isOpened())

ret = True

while (cap.isOpened()):
    ret, frame = cap.read()
    if ret == True:
        new_cap.write(frame)

    else:
        # cap.release()
        new_cap.release()
        break




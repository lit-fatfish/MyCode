import cv2 
import os, sys
import numpy as np
from PIL import Image, ImageFont, ImageDraw


src_video = sys.argv[1]
dst_video = sys.argv[2]
start_time = sys.argv[3]
end_time = sys.argv[4]


cut_video_cmd = "ffmpeg  -ss " + str(start_time) + " -i " + src_video + " -t  " + str(end_time) + " -c copy -f mp4 -y " + dst_video
val = os.system(cut_video_cmd)
# os.popen(cut_video_cmd)

# 本文件用于在一张图片，添加文字和画框

import os, cv2
import darknet as dn
import numpy as np
from PIL import Image, ImageFont, ImageDraw



def paint_chinese_opencv(im,chinese,pos,color, fontsize):
  img_PIL = Image.fromarray(cv2.cvtColor(im,cv2.COLOR_BGR2RGB))
  font = ImageFont.truetype('NotoSansCJK-Bold.ttc', fontsize)
  fillColor = color #(255,0,0)
  position = pos #(100,100)
  if not isinstance(chinese,str):
      chinese = chinese.decode('utf-8')
  draw = ImageDraw.Draw(img_PIL)
  draw.text(position, chinese, font=font, fill=fillColor)
  img = cv2.cvtColor(np.asarray(img_PIL),cv2.COLOR_RGB2BGR)
  return img


img_src_path = "/home/anlly/workspace/nas_project/keimy/data_building/20200827_building/smoke/record_miku5_20200827094638_X_KE000504.jpg"
img_dst_path = "/home/anlly/workspace/nas_project/keimy/data_building/20200827_building/smoke_dist/record_miku5_20200827094638_X_KE000504.jpg"

img = cv2.imread(img_src_path)
img = paint_chinese_opencv(img, "云景黑烟事件", (20,640), (255, 255, 255), 24)
img = paint_chinese_opencv(img, "违规车牌编码：X-KE000504", (20,670), (255, 255, 255), 24)

# 

pt1 = (586, 466)    # 左上角
pt2 = (669, 486)    # 右下角
color = (0, 0, 255)

cv2.rectangle(img, pt1, pt2, color, 2)


cv2.imwrite(img_dst_path, img)
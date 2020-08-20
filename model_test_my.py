from detection_video import load_test_model, detection_video
from utils import load_config
import argparse
import os, cv2
import darknet as dn

def convertBack(x, y, w, h):
  xmin = int(round(x - (w / 2)))
  xmax = int(round(x + (w / 2)))
  ymin = int(round(y - (h / 2)))
  ymax = int(round(y + (h / 2)))
  return xmin, ymin, xmax, ymax

def cvDrawBoxes(detections, img):
  print("detections", detections)
  for detection in detections:
    print("detection",detection)
    if detection[0] == b'car':
      continue
    model_name = detection[0]
    if detection[0] == b'person':
      model_name = b'unsafe'

    x, y, w, h = detection[2][0],\
      detection[2][1],\
      detection[2][2],\
      detection[2][3]
    xmin, ymin, xmax, ymax = convertBack(
      float(x), float(y), float(w), float(h))
    pt1 = (xmin, ymin)
    pt2 = (xmax, ymax)
    color = (255, 0, 0)
    txt_color = [255, 0, 0]

    if detection[0] == b'hat':
      txt_color = [0, 255, 0]
      color = (0, 255, 0)

    cv2.rectangle(img, pt1, pt2, color, 3)
    cv2.putText(img,
      model_name.decode(),
      (pt1[0], pt1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.8,
      txt_color, 2)
  return img


parser = argparse.ArgumentParser()
# parser.add_argument("-model_name", "--model_name",type=str,help="model_name", default="smoke_append_20200213")
parser.add_argument("-src_path", "--src_path", type=str,help="src path", default="/home/anlly/workspace/nas_project/keimy/data_building/20200818_building_dist/hat_test")
parser.add_argument("-dist_path", "--dist_path", type=str,help="dist path",default="/home/anlly/workspace/nas_project/keimy/data_building/20200818_building_dist/hat_test_dist_new")
# parser.add_argument('-output_img', "--output_img", help='output bingo images', default=0, type=int)
# parser.add_argument('-output_txt', "--output_txt", help='output bingo txt', default=0, type=int)
# parser.add_argument('-save_img_thres', "--save_img_thres", help='save img thres', default=5, type=int)
parser.add_argument('-model_path', "--model_path", help='model_path', type=str,default="/home/anlly/workspace/rtx_train_data/building_site/hat/20200815_hat")
parser.add_argument('-weights_path', "--weights_path", help='weights path', type=str,default="/home/anlly/workspace/rtx_train_data/building_site/hat/20200815_hat/backup/voc_10000.weights")

args = parser.parse_args()

# 文件输入路径
src_path = args.src_path
# 文件输出路径
dist_path = args.dist_path
# 获取输入文件列表
detection_src_list = os.listdir(src_path)
# 推理数据文件
detection_file_path = os.path.join(args.dist_path, 'result.txt')
# 模型路径
model_path = args.model_path
# 权重路径
weight_path = args.weights_path

print("src_path", src_path)
print("dist_path", dist_path)
print("detection_src_list", detection_src_list)
print("detection_file_path", detection_file_path)
print("model_path",model_path)
print("weight_path", weight_path)

# exit(0)

if os.path.exists(detection_file_path):
  os.remove(detection_file_path)

fd = open(detection_file_path, mode="w", encoding="utf-8")
fd.close()

# 获取模型
model_data = {
	"cfg": os.path.join(model_path, "voc_test.cfg"),
	"data": os.path.join(model_path, "voc.data"),
	"category": os.path.join(model_path, "voc.names"),
	"weights": weight_path
}
print("model_data", model_data)
# exit(0)
# load model VIDEO
# detection_model = load_test_model(model_data)
# netMain = detection_model['netMain']
# metaMain = detection_model['metaMain']
# altNames = detection_model['altNames']

print("加载 video 模型完成")

# set GPU
dn.set_gpu(0)
# load model IMG
net = dn.load_net(bytes(model_data['cfg'], 'utf-8'), bytes(model_data['weights'], 'utf-8'), 0)
meta = dn.load_meta(bytes(model_data['data'], 'utf-8'))

print("加载 img 模型完成")

for item in detection_src_list:
  print("item: ", item)
  if item == 'DJI_2021.mp4':
    continue
  srcFilePath = os.path.join(src_path, item)
  outputRectFilePath = os.path.join(dist_path, item)

  if item.endswith('.wh264') or item.endswith('.mp4'):
    cap = cv2.VideoCapture(srcFilePath)
    return_value, frame = cap.read()
    if return_value == False:
      print("视频识别失败")
      continue

    size = [frame.shape[1], frame.shape[0]]
    print("video size: ", size)

    if size[0] > 1920:
      size[0] = 1920
    if size[1] > 1080:
      size[1] = 1080

    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    out = cv2.VideoWriter(outputRectFilePath, fourcc, 25.0, (size[0], size[1]))
    # Create an image we reuse for each detect
    
    darknet_image = dn.make_image(size[0], size[1], 3)

    run_bool = True

    while run_bool:
      ret, frame_read = cap.read()
      
      if ret == False:
        break
      # frame_read = cv2.resize(frame_read, (size[0], size[1]))
      frame_rgb = cv2.cvtColor(frame_read, cv2.COLOR_BGR2RGB)
      dn.copy_image_from_bytes(darknet_image, frame_rgb.tobytes())
      # detections = dn.detect_image(netMain, metaMain, darknet_image, thresh=0.80)
      detections = dn.detect_image(net, meta, darknet_image, thresh=0.80)
      image = cvDrawBoxes(detections, frame_rgb)
      if (len(detections)):
        print("*", end='')
      else:
        print("#", end='')

      image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
      out.write(image)

    cap.release()
    out.release()

  else:
    print("开始推理 img")
    detections = dn.detect(net, meta, bytes(srcFilePath, 'utf-8'), thresh=0.8)
    print("推理 img 完成")
    img = cv2.imread(srcFilePath)
    # img = cv2.resize(img, (1920, 1080))
    img = cvDrawBoxes(detections, img)
    cv2.imwrite(outputRectFilePath, img)
  
  with open(detection_file_path, 'a+') as f:
    f.write(item + '\n')

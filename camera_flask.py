import json, os
from route import camera_blue
from extend.rabbitMQ import Rabbit
from flask import request
from extend.variables import Variables
from extend.utils import Utils

rabbit = Rabbit()           # rabbitMQ
var = Variables()           # 初始化变量
utils = Utils()             # 初始化工具函数

# 刷新网点黑度
def refresh_data():
  camera_list = utils.load_json(var.config_path['camera_list'])
  camera_dots = [item['dot_id'] for item in camera_list['camera_list']]
  darkness_level = utils.load_yaml(var.config_path['darkness_level'])
  new_darkness_level = {"camera": {}}
  for item in camera_dots:
    dot_exists = False
    for its in darkness_level['camera']:
      if its == item:
        dot_exists = True
        new_darkness_level['camera'][item] = darkness_level['camera'][its]
        break
    if not dot_exists:
      new_darkness_level['camera'][item] = {
        0: 0,
        1: 20,
        2: 40,
        3: 60,
        4: 80,
        5: 100
      }

  utils.write_yaml(var.config_path['darkness_level'], new_darkness_level)


@camera_blue.route('/api/get_list', methods=["GET","POST"])
def get_list():
  camera_list = utils.load_json(var.config_path['camera_list'])
  data = {
    'status': 200,
    'camera_list': camera_list['camera_list']
  }
  return json.dumps(data)

@camera_blue.route('/api/add_camera', methods=["GET","POST"])
def add_camera():
  camera_list = utils.load_json(var.config_path['camera_list'])
  if request.method == 'POST':

    get_data = json.loads(request.get_data())
    camera_ip = get_data['camera_ip']
    camera_user = get_data['camera_user']
    camera_pwd = get_data['camera_pwd']
    dot_id = get_data['dot_id']
    status = get_data['status']
    dn_rtsp = get_data['dn_rtsp']
    camera_rtsp = "rtsp://{}:{}@{}/h264/main/sub/av_stream".format(camera_user, camera_pwd, camera_ip)

    is_append = True
    for item in camera_list['camera_list']:
      if item['camera_ip'] == camera_ip:
        is_append = False
        break

    if is_append:
      camera_list['camera_list'].append({
        "camera_ip": camera_ip,
        "camera_user": camera_user,
        "camera_pwd": camera_pwd,
        "dot_id": dot_id,
        "camera_rtsp": camera_rtsp,
        "dn_rtsp":dn_rtsp,
        "status": status
      })

  with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
    json.dump(camera_list, f, indent=2)

  refresh_data()
  data = {
    'status': 200,
    'msg': 'add camera successfully'
  }
  return json.dumps(data)

@camera_blue.route('/api/del_camera', methods=["GET","POST"])
def del_camera():
  camera_list = utils.load_json(var.config_path['camera_list'])
  if request.method == 'POST':
    get_data = json.loads(request.get_data())
    camera_ip = get_data['camera_ip']
    for item in camera_list['camera_list']:
      if item['camera_ip'] == camera_ip:
        camera_list['camera_list'].remove(item)
        break

  with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
    json.dump(camera_list, f, indent=2)

  refresh_data()
  data = {
    'status': 200,
    'msg': 'del camera successfully'
  }
  return json.dumps(data)

@camera_blue.route('/api/update_camera', methods=["GET","POST"])
def update_camera():
  camera_list = utils.load_json(var.config_path['camera_list'])
  if request.method == 'POST':
    get_data = json.loads(request.get_data())
    print(get_data)
    camera_ip = get_data['camera_ip']
    camera_user = get_data['camera_user']
    camera_pwd = get_data['camera_pwd']
    dot_id = get_data['dot_id']
    status = get_data['status']
    dn_rtsp = get_data['dn_rtsp']
    camera_rtsp = "rtsp://{}:{}@{}/h264/main/sub/av_stream".format(camera_user, camera_pwd, camera_ip)

    for index, item in enumerate(camera_list['camera_list']):
      if item['camera_ip'] == camera_ip:
        camera_list['camera_list'][index] = {
          "camera_ip": camera_ip,
          "camera_user": camera_user,
          "camera_pwd": camera_pwd,
          "dot_id": dot_id,
          "camera_rtsp": camera_rtsp,
          "status": status,
          "dn_rtsp":dn_rtsp
        }
        break
  with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
    json.dump(camera_list, f, indent=2)

  refresh_data()

  data = {
    'status': 200,
    'msg': 'update camera successfully'
  }
  return json.dumps(data)

@camera_blue.route('/api/camera_controll', methods=["GET","POST"])
def camera_controll():
  camera_list = utils.load_json(var.config_path['camera_list'])
  if request.method == 'POST':
    get_data = json.loads(request.get_data())
    camera_ip = get_data['camera_ip']
    camera_user = get_data['camera_user']
    camera_pwd = get_data['camera_pwd']
    dot_id = get_data['dot_id']
    dn_rtsp = get_data['dn_rtsp']
    print(get_data)
    if get_data["controll"] == 0:
      print("start")
      
      command = "ps -ef | grep -v grep | grep " + camera_ip + " | awk '{print $2}' | wc -l"

      camera_run_bool = os.popen(command).read()
      if not int(camera_run_bool):
        camera_rtsp = "rtsp://{}:{}@{}/h264/main/sub/av_stream".format(camera_user, camera_pwd, camera_ip)
        run_camera = 'nohup python /home/anlly/Ring/rath/darkness.py {} {} {} > output_darness.log 2>&1'.format(dn_rtsp, camera_rtsp, dot_id)
        os.popen(run_camera)
        # 打开计量推理
        # 修改状态
        camera_list = utils.load_json(var.config_path['camera_list'])
        for index, item in enumerate(camera_list['camera_list']):
          if item['camera_ip'] == camera_ip:
            camera_list['camera_list'][index]["status"] =  1          
            break
        with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
          json.dump(camera_list, f, indent=2)
    elif get_data["controll"] == 1:
      # 关闭
      print("close")
      close_camera = "ps -ef | grep -v grep | grep " +  camera_ip + " | awk '{print $2}' | xargs kill"
      os.popen(close_camera)
      camera_list = utils.load_json(var.config_path['camera_list'])
      for index, item in enumerate(camera_list['camera_list']):
        if item['camera_ip'] == camera_ip:
          camera_list['camera_list'][index]["status"] =  0          
          break
      with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
        json.dump(camera_list, f, indent=2)
  data = {
    'status': 200,
    'msg': 'run camera successfully'
  }
  return json.dumps(data)


@camera_blue.route('/api/cal_status', methods=["GET","POST"])
def cal_status():
  data = {}
  if request.method == 'POST':
    get_data = json.loads(request.get_data())
    print(get_data)
    print(get_data["data"])
    # return json.dumps(data)
    if get_data["data"]["status"] == 1:
      data["status"] = "open"
    elif get_data["data"]["status"] == 0:
      data["status"] = "close"

  return json.dumps(data)
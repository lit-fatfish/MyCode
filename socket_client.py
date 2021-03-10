#!/usr/bin/python3
# 文件名：client.py

# 导入 socket、sys 模块
import json
import socket
import sys

# 创建 socket 对象
import time



# 获取本地主机名
host = socket.gethostname() 

# 设置端口号
port = 9999

host = "111.230.129.137"
port = 6152

num = 0
while 1:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 连接服务，指定主机和端口
    s.connect((host, port))
    print(host, port)
    # 接收小于 1024 字节的数据
    # msg = s.recv(1024)
    # print(msg)
    # data = {"type":"3dmove","x": 100, "y": 100,  "cameraid":  9  , "width":1920, "height": 1080, "num":num}
    data = {"type":"test","x": 100, "y": 100,  "cameraid":  9  , "width":1920, "height": 1080, "num":num}
    # s.send("hello world".encode())
    head_data = json.dumps(data) 
    s.send(head_data.encode())
    s.send(head_data.encode())


    time.sleep(1)
    # print (msg.decode('utf-8'))
    num += 1
    # s.close()
    if num >= 10:
        exit(0)



#!/usr/bin/python3
# 文件名：server.py

# 导入 socket、sys 模块
import socket
import sys

# 创建 socket 对象
serversocket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM) 

# 获取本地主机名
host = socket.gethostname()

port = 9999

# 绑定端口号
serversocket.bind((host, port))

# 设置最大连接数，超过后排队
serversocket.listen(5)


def unpack(recv_str):
    # print("in unpack", recv_str)
    # if recv_str[:5] == "start":
    #     print("in ok")
    for index, item in enumerate(recv_str):
        if item == '{':
            start_index = index
        elif item == '}':
            end_index = index + 1
            print(recv_str[start_index:end_index])
            return recv_str[end_index:]
    return 0



while True:
    # 建立客户端连接
    clientsocket,addr = serversocket.accept()      

    print("连接地址: %s" % str(addr))
    
    # msg='欢迎访问菜鸟教程！'+ "\r\n"
    recv = clientsocket.recv(1024)
    print(recv.decode()[0:5])
    new_recv = recv.decode()
    new_recv = unpack(new_recv)
    while new_recv:
        new_recv = unpack(new_recv)
        
    # if new_recv[0:5] == "start":
    #     for index, item in enumerate(new_recv[5:]):
    #         if item == '{':
    #             start_index = index + 5
    #         elif item == '}':
    #             end_index = index + 6
    #             print(new_recv[start_index:end_index])
    #             break
            

    # if recv[0:7] == "{'type'":
    #     print("ok")
        # for item in recv.decode():  
        #     print(item)
        
    print(recv.decode())
    # clientsocket.send(msg.encode('utf-8'))
    clientsocket.close()
clientsocket.close()
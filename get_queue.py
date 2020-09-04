import redis
import json
import time
from extend.rabbitMQ import Rabbit
from extend.variables import Variables
import requests
import threading
# 目标，循环读redis，然后获取数据

global_result = {}

var = Variables()



def consumer_img(ch, method, properties, body):
    global global_result
    ch.basic_ack(delivery_tag=method.delivery_tag)
    result = json.loads( body.decode() )
    print("consumer_img: ", result, type(result))

    global_result = result

def consumer_thread():
    rabbit = Rabbit()
    rabbit.consumer(var.rabbitmq_queue['result_black'], consumer_img)

def thread_start():
    t = threading.Thread(target=consumer_thread)
    t.start()

thread_start()

# 根据键值读字符串
def get_values(r, key):
    dic = r.get(key)
    if dic :
        return eval(dic)
    else:
        return False

# dic 字典
def set_values(r, key, dic):
    r.set(key, json.dumps(dic)) # 获取到期天数，然后乘以86400s（一天）


# 成功返回int 1
def remove_key(r, key):
    return r.delete(key)


# callback_obj字典对象
def write_queue(r,queue_name, callback_obj):
    callback_obj = json.dumps(callback_obj)
    callback_mapping = {
        callback_obj: time.time()
    }
    r.zadd(queue_name, callback_mapping)


def read_queue(r,queue_name):
    range_list = r.zrange(queue_name, 0, 1)
    if range_list:
        set_del_task = range_list[0]
        set_del_task = json.loads(set_del_task)
        return set_del_task


def remove_queue(r,queue_name, callback_obj):
    callback_obj = json.dumps(callback_obj)
    r.zrem(queue_name,callback_obj)


def init_redis():
    pwd = "anlly12345"
    host = '192.168.31.19'
    db = 8
    # host = 'localhost'
    # pwd = ''
    redis_obj = redis.Redis(host=host, port=6379, password=pwd, db=db, decode_responses=True)
    return redis_obj


def mian():

    r = init_redis()
    # 检测Redis中待推理的进程

    # 假如key:values 中type的值为2，则开始计量

    # 删除等待队列

    # 加入推理中队列

    # 开始录制视频，发送RabbitMQ

    # 发送结束信号？

    # 等待接受信号

    # 将数据写入Redis中的回调队列
    while(1):
        time.sleep(1)
        zset = read_queue(r, "waitReasoningList")
        print(zset)
        if not zset:
            continue
        key = "dot_info:" + str(zset)
        values = get_values(r, key)
        if not values:
            continue

        print("values", values)

        # 计量
        if values["type"] == 2:
            print("ok")
            # 删除队列等待队列
            remove_queue(r, "waitReasoningList",zset)
            # remove_key(r,key)

            # 加入待推理中
            write_queue(r, "reasoningList", zset)
            # set_values(r,)

            # filename = 
            # 开始录像
            filename = str(int(time.time()))
            source_name = "source_" + filename +  ".mp4"
            dist_name = "dist_" + filename +  ".mp4"
            formdata = {
                "type": "start", 
                "source_name": source_name,
                "dist_name": dist_name
            }
            url = "http://192.168.31.19:8001/record"
            try:
                response = requests.post(url, data=json.dumps(formdata))
                print(response.text)
                json_result = response.json()
                print("start", json_result)
                if json_result["status"] == 200:
                    # time.sleep(10)
                    for i in range(10):
                        time.sleep(1)
                        print(10-i)
                    formdata["type"] = "stop"
                    response = requests.post(url, data=json.dumps(formdata))
                    json_result = response.json()
                    print("stop", json_result)
            except:
                print("error")
                continue

            time.sleep(1)
            dic = {
                "type":values["type"],
                "result":global_result,
                "callback":"https://power.anlly.net/customer/api/v1/callback"

            }
            print("dic",dic)

            # 等待录制结束加入待回调中
            remove_queue(r, "reasoningList", zset)
            write_queue(r,"callbackList", zset)
            # 写入key_value

            set_values(r, key, dic)





if __name__ == '__main__':
    mian()
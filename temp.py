import redis, json, time
from extend.rabbitMQ import Rabbit
from extend.variables import Variables
from extend.utils import Utils
import requests
import threading, os

from extend.redis_tools import RedisTools

var = Variables()
utils = Utils()

r = RedisTools("172.17.0.1", 6379, "anlly12345", 8)


class GetQueue():
    def __init__(self):
        pass
        self.result = {}
        self.open_flag = 0  # 开启自动跟踪标志位
        self.task_id = 0
        self.line = {
            "0":{
                "1":0,
                "2":0,
                "3":0
            }
        }

    def consumer_result_black(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        result = json.loads(body.decode())
        print("consumer_result_black: ", result, type(result))

        # self.result = result
        # 处理计量得到的结果
        dot_id = result["dot_id"]
        dic = {
            "type":"2",
            "result":result,
            "callback":"https://power.anlly.net/customer/api/v1/callback"

        }
        # 等待录制结束加入待回调中
        r.remove_queue("reasoningList", dot_id)
        r.write_queue("callbackList", dot_id)
        # 写入key_value
        key = "dot_info:" + dot_id
        r.set_values(key, dic)
        # 清除标志位
        self.line["0"] = {
                "1":0,
                "2":0,
                "3":0
        }

    

    def consumer_thread(self):
        rabbit = Rabbit()
        rabbit.consumer(var.rabbitmq_queue['result_black'], self.consumer_result_black)

    

    def consumer_find_board(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        result = json.loads(body.decode())
        print("consumer_result_black: ", result, type(result))

        # self.result = result
        # 处理找板得到的结果
        
        isboard = result["is_board"]
        self.task_id = result["task_id"]
        dot_id = result["camera"]

        if isboard == 1:
            
            for item in self.line[self.task_id]:
                # 判断是否存在1
                if self.line[self.task_id][item] == 1:
                    return False
                    
            self.line[self.task_id]["dot_id"] = 1            
        else:
            print("not found board")
            return


        camera_list = utils.load_json(var.config_path['camera_list'])
        for index, item in enumerate(camera_list['camera_list']):
            if item['dot_id'] == dot_id:
                dn_rtsp = item["dn_rtsp"]
                camera_rtsp = item["camera_rtsp"]
                dot_id = item["dot_id"]
                # 调用计量程序，线程
                self.measurement_thread(dot_id, dn_rtsp,camera_rtsp, dot_id, task_id)
                break

        
    def consumer_board_thread(self):
        rabbit = Rabbit()
        rabbit.consumer(var.rabbitmq_queue['result_black'], self.consumer_result_black)
    
    def thread_start(self):
        t = threading.Thread(target=self.consumer_thread)
        t.start()
        t = threading.Thread(target=self.consumer_board_thread)
        t.start()


    def check_find_board(self):
        # 根据配置文件开启或者关闭程序
        camera_list = utils.load_json(var.config_path['camera_list'])
        # print(camera_list)
        for index, item in enumerate(camera_list['camera_list']):
            dn_rtsp = camera_list['camera_list'][index]["dn_rtsp"]
            camera_rtsp = camera_list['camera_list'][index]["camera_rtsp"]
            dot_id = camera_list['camera_list'][index]["dot_id"]
            if camera_list['camera_list'][index]["track_bool"] == 1:
                if self.open_flag == 0:
                    # 开启程序
                    print(dot_id, "open find_board")
                    run_camera = 'nohup python /root/app/find_board.py {} {} {} > output_find_board.log 2>&1'.format(
                        dn_rtsp, camera_rtsp, dot_id)
                    # print(run_camera)
                    os.popen(run_camera)
                    self.open_flag = 1
                elif self.open_flag == 1:
                    # 监控程序，假如不在的话，修改配置文件，并设置open_flag =0

                    # 检测是否打开
                    command = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | wc -l"
                    # print(command)
                    camera_run_bool = os.popen(command).read()
                    if not int(camera_run_bool):
                        # 修改配置文件
                        camera_list['camera_list'][index]["track_bool"] = 0
                        with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
                            json.dump(camera_list, f, indent=2)
                        self.open_flag = 0
                        print(dot_id, "close find_board")
            elif camera_list['camera_list'][index]["track_bool"] == 0:
                command = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | wc -l"
                # print(command)
                camera_run_bool = os.popen(command).read()
                if int(camera_run_bool) and self.open_flag == 1:
                    close_camera = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | xargs kill"

                    os.popen(close_camera)
                    # print("close_camera", close_camera)
                    print(dot_id, "close find_board")
                    self.open_flag = 0

    # 找板，等待到结束，主函数调用也会等待
    def find_board(self, dn_rtsp, camera_rtsp, dot_id):

        run_camera = 'nohup python /root/app/find_board.py {} {} {} > output_find_board.log 2>&1'.format(dn_rtsp,
                                                                                                         camera_rtsp,
                                                                                                         dot_id)
        os.popen(run_camera)

        # overtime = 30
        # camera_run_bool = 1

        # while overtime > 0 and camera_run_bool != 0:
        #     overtime -= 1
        #     time.sleep(1)
        #     command = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | wc -l"
        #     camera_run_bool = os.popen(command).read()
        #     # 结束
        #     if not int(camera_run_bool):
        #         # 说明程序结束了
        #         pass
        # pass
        # # 找到板
        # return overtime



    # 开启计量程序
    def measurement (self, zset, dn_rtsp, camera_rtsp, dot_id, task_id):
        pass
        # 根据调用的id和type开启一个计量线程

        # 找板
        # overtime = self.find_board(dn_rtsp, camera_rtsp, dot_id, task_id)
        # 等待找板结束

        # 判断开启那一个
        # 情况分类
        '''
            首先判断返回的超时时间，得出当前球机是否找到了板
            然后判断你的兄弟球机的找板函数是否在运行
                假如在的话就是你先运行。
                假如不在的话就是已经有程序在运行了。
        '''
        # 超时时间大于0，说明找到了板
        # if overtime > 0:
        #     # 判断兄弟球机的找板函数状态
        #     command = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | wc -l"
        #     camera_run_bool = os.popen(command).read()

        # 判断那一个程序进入计量/测烟

        # 开启计量
        blacktest_id = "blacktest_" + dot_id
        filename = str(int(time.time()))
        source_name = "source_" + filename + ".mp4"
        dist_name = "dist_" + filename + ".mp4"
        formdata = {
            "type": "start",
            "source_name": source_name,
            "dist_name": dist_name,
            "camera": zset
        }
        rabbit = Rabbit()           # rabbitMQ
        rabbit.create_queue(blacktest_id, formdata)

        time_length = 10
        for i in range(time_length):
            time.sleep(1)
            print(time_length - i)
        formdata["type"] = "stop"
        rabbit.create_queue(blacktest_id, formdata)       

    def measurement_thread(self, zset, dn_rtsp, camera_rtsp, dot_id, task_id):
        t = threading.Thread(target=measurement, args=(self, zset, dn_rtsp, camera_rtsp, dot_id, task_id,))
        t.start()

    def loop_scan(self):

        while True:
            time.sleep(1)
            # 读队列
            zset = r.read_queue("waitReasoningList")
            if not zset:
                continue
            key = "dot_info:" + str(zset)
            values = r.get_values(key)
            if not values:
                r.remove_queue("waitReasoningList")
                continue
            # 计量
            if int(values["type"]) == 2:
                # 删除队列等待队列
                r.remove_queue("waitReasoningList",zset)
                # 加入待推理中
                r.write_queue("reasoningList", zset)


                # 根据网点查找参数
                camera_list = utils.load_json(var.config_path['camera_list'])
                for index, item in enumerate(camera_list['camera_list']):
                    if item['dot_id'] == zset:
                        dn_rtsp = item["dn_rtsp"]
                        camera_rtsp = item["camera_rtsp"]
                        dot_id = item["dot_id"]
                        # 启动线程
                        task_id = str(int(dot_id)/3)
                        # self.measurement(zset, dn_rtsp, camera_rtsp, dot_id, task_id)    # 修改为线程函数
                        self.find_board(dn_rtsp, camera_rtsp, dot_id, task_id)  # 启动找板程序
                        break
            # 测烟
            if int(values["type"]) == 1:
                pass
    
    


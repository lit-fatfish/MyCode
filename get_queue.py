import redis, json, time
from extend.rabbitMQ import Rabbit
from extend.variables import Variables
from extend.utils import Utils
import requests
import threading, os

from extend.redis_tools import RedisTools

var = Variables()
utils = Utils()

utils.timing_check_darkness(5)
r = RedisTools("172.17.0.1", 6379, "anlly12345", 8)


class GetQueue():
    def __init__(self):
        pass
        self.result = {}
        self.open_flag = 0  # 开启自动跟踪标志位
        # task = "0"
        self.line = {
            "1":{
                "1":0,
                "2":0,
                "3":0
            },
            "2":{
                "4":0,
                "5":0,
                "6":0
            },
            "3":{
                "7":0,
                "8":0,
                "9":0
            }
        }
            
# ----------------------处理计量结果--------------------------------------
    def consumer_result_black(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        result = json.loads(body.decode())
        print("consumer_result_black: ", result, type(result))

        dot_id = int(result["dot_id"])  # 网点id
        key = "dot_info:" + str(dot_id) # 网点id对应的key
        dic = r.get_values(key)        # values
        if not dic:
            return False
        print("dic", dic)


        # self.result = result
        # 处理计量得到的结果
        dic["result"] = result
        dic["callback"] = "https://power.anlly.net/customer/api/v1/callback"
        dic["result"].pop("dot_id")
        # 等待录制结束加入待回调中
        r.remove_queue("reasoningList", dot_id)
        r.write_queue("callbackList", dot_id)
        # 写入key_value
        
        r.set_values(key, dic)
        # 清除标志位
        task_id = str(int((dot_id + 2)/3))
        self.line[task_id] = {
            "1":0,
            "2":0,
            "3":0
        }

    

    def consumer_thread(self):
        rabbit = Rabbit()
        rabbit.consumer(var.rabbitmq_queue['result_black'], self.consumer_result_black)

    # --------------------处理找板结果-------------------------------
    
    def find_dot_num(self, line_id):
        # 根据厂线得出，当前配置有多少个摄像头，用做没找到板时的判断
        count = 0
        camera_list = utils.load_json(var.config_path['camera_list'])
        for index, item in enumerate(camera_list['camera_list']):
            if item['line_id'] == line_id:
                count += 1
        return count


    def consumer_find_board(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        result = json.loads(body.decode())
        print("consumer_find_board: ", result, type(result))

        # self.result = result
        # 处理找板得到的结果
        
        isboard = result["is_board"]
        task_id = result["task_id"]
        dot_id = result["camera"]

        print("line", self.line)
        print("task_id", task_id)
        print("dot_id", dot_id)

        zset = int(dot_id)
        key = "dot_info:" + dot_id
        values = r.get_values(key)
        if not values:
            print("not found redis data")
            return False
        
        # 判断是否为计量，假如是计量 type = 2,执行计量程序（每个都要）
        if int(values["type"]) == 2:
            print("is jiliang ")
        else:
            # 进来就是2，假如找到了就是1
            self.line[task_id][dot_id] = 2
            if int(isboard) == 1:
                
                for item in self.line[task_id]:
                    # print("item",item)
                    # 判断是否存在1
                    if self.line[task_id][item] == 1:
                        print("other program in running")
                        return False
                        
                self.line[task_id][dot_id] = 1            
            else:
                print("not found board")
                dot_num = self.find_dot_num(task_id)
                count = 0
                for item in self.line[task_id]:
                    # print("item",item)
                    # 判断三个是否都是2，不是的话就不执行，是的话就执行当前这个
                    if self.line[task_id][item] == 2:
                        count += 1
                print("count=",count)
                if count == dot_num:
                    # 都没有找到
                    print("all not found board")
                    pass
                else:
                    return False


        camera_list = utils.load_json(var.config_path['camera_list'])
        for index, item in enumerate(camera_list['camera_list']):
            if item['dot_id'] == dot_id:
                dn_rtsp = item["dn_rtsp"]
                camera_rtsp = item["source_rtsp"]
                dot_id = item["dot_id"]
                # 调用计量程序，线程
                
                if int(values["type"]) == 1:
                    print(dot_id, "run darkness program")
                    # 启动测烟程序
                    test_black = 'nohup python /root/app/rath.py {} {} {} > /dev/null 2>&1'.format(dn_rtsp, camera_rtsp, dot_id)
                    os.popen(test_black)

                elif int(values["type"]) == 2:
                    print(dot_id, "run jiliang program")
                    self.measurement_thread(dot_id, dn_rtsp,camera_rtsp, dot_id, task_id)
                break

        
    def consumer_board_thread(self):
        rabbit = Rabbit()
        rabbit.consumer("find_board", self.consumer_find_board)
    




    # ----------------------处理正常测烟结果-----------------------------

    def consumer_dn_darkness_result(self, ch, method, properties, body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        result = json.loads(body.decode())
        print("consumer_dn_darkness_result: ", result, type(result))

        dot_id = int(result["dot_id"])  # 网点id
        key = "dot_info:" + str(dot_id) # 网点id对应的key
        dic = r.get_values(key)        # values
        if not dic:
            return False
        print("dic", dic)


        # self.result = result
        # 处理计量得到的结果
        dic["result"] = result
        dic["callback"] = "https://power.anlly.net/customer/api/v1/callback"
        dic["result"].pop("dot_id")
        # 等待录制结束加入待回调中
        r.remove_queue("reasoningList", dot_id)
        r.write_queue("callbackList", dot_id)
        # 写入key_value
        
        r.set_values(key, dic)
        # 清除标志位

        task_id = str(int((dot_id + 2)/3))
        self.line[task_id] = {
            "1":0,
            "2":0,
            "3":0
        }
        print("darkness test finish")

    

    def consumer_darkness_thread(self):
        rabbit = Rabbit()
        rabbit.consumer("dn_darkness_result", self.consumer_dn_darkness_result)


    def thread_start(self):
        t = threading.Thread(target=self.consumer_thread)
        t.start()
        t = threading.Thread(target=self.consumer_board_thread)
        t.start()
        t = threading.Thread(target=self.consumer_darkness_thread)
        t.start()

    # 没用到，查不多要删除了
    # def check_find_board(self):
    #     # 根据配置文件开启或者关闭程序
    #     camera_list = utils.load_json(var.config_path['camera_list'])
    #     # print(camera_list)
    #     for index, item in enumerate(camera_list['camera_list']):
    #         dn_rtsp = camera_list['camera_list'][index]["dn_rtsp"]
    #         camera_rtsp = camera_list['camera_list'][index]["source_rtsp"]
    #         dot_id = camera_list['camera_list'][index]["dot_id"]
    #         if camera_list['camera_list'][index]["track_bool"] == 1:
    #             if self.open_flag == 0:
    #                 # 开启程序
    #                 print(dot_id, "open find_board")
    #                 run_camera = 'nohup python /root/app/find_board.py {} {} {} > output_find_board.log 2>&1'.format(
    #                     dn_rtsp, camera_rtsp, dot_id)
    #                 # print(run_camera)
    #                 os.popen(run_camera)
    #                 self.open_flag = 1
    #             elif self.open_flag == 1:
    #                 # 监控程序，假如不在的话，修改配置文件，并设置open_flag =0

    #                 # 检测是否打开
    #                 command = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | wc -l"
    #                 # print(command)
    #                 camera_run_bool = os.popen(command).read()
    #                 if not int(camera_run_bool):
    #                     # 修改配置文件
    #                     camera_list['camera_list'][index]["track_bool"] = 0
    #                     with open(var.config_path['camera_list'], 'w', encoding='utf8')as f:
    #                         json.dump(camera_list, f, indent=2)
    #                     self.open_flag = 0
    #                     print(dot_id, "close find_board")
    #         elif camera_list['camera_list'][index]["track_bool"] == 0:
    #             command = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | wc -l"
    #             # print(command)
    #             camera_run_bool = os.popen(command).read()
    #             if int(camera_run_bool) and self.open_flag == 1:
    #                 close_camera = "ps -ef | grep -v grep | grep " + dn_rtsp + " | grep find_board.py | awk '{print $2}' | xargs kill"

    #                 os.popen(close_camera)
    #                 # print("close_camera", close_camera)
    #                 print(dot_id, "close find_board")
    #                 self.open_flag = 0

    # 找板，等待到结束，主函数调用也会等待
    def find_board(self, dn_rtsp, camera_rtsp, dot_id, task_id, test_type):
        print("in find_board function")

        run_camera = 'nohup python /root/app/find_board.py {} {} {} {} {} > output_find_board.log 2>&1'.format(dn_rtsp,
                                                                                                         camera_rtsp,
                                                                                                         dot_id,
                                                                                                         task_id,
                                                                                                         test_type)
        os.popen(run_camera)





    # 开启计量程序
    def measurement (self, zset, dn_rtsp, camera_rtsp, dot_id, task_id):
       
        
        print("dot_id=",dot_id, "darkness start")

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
        t = threading.Thread(target=self.measurement, args=(zset, dn_rtsp, camera_rtsp, dot_id, task_id,))
        t.start()

    # 结束测烟程序
    def end_black_test(self, dot_id):

        dn_darkness_id = "dn_darkness_" + dot_id
        stop_data = {
            "type": "stop"
        }
        print("dn_darkness_id=", dn_darkness_id, "close black test")
        # print("stop_data=", stop_data)
        rabbit = Rabbit()           # rabbitMQ
        rabbit.create_queue(dn_darkness_id, stop_data)

    def loop_scan(self):

        while True:
            time.sleep(1)
            # 读队列
            # self.check_find_board()
            zset = r.read_queue("waitReasoningList")
            end_signal = r.read_queue("reasoningEndList")
            if end_signal :
                r.remove_queue("reasoningEndList", end_signal)
                self.end_black_test(str(end_signal))
            if not zset:
                continue
            # print(type(zset))
            
            key = "dot_info:" + str(zset)
            values = r.get_values(key)
            if not values:
                r.remove_queue("waitReasoningList")
                continue

            # values["serial"] # 流水号
            # 计量
            if int(values["type"]) == 1 or int(values["type"]) == 2:
                print("start wait queue")
                # 删除队列等待队列
                r.remove_queue("waitReasoningList",zset)
                # 加入待推理中
                r.write_queue("reasoningList", zset)


                # 根据网点查找参数
                camera_list = utils.load_json(var.config_path['camera_list'])
                for index, item in enumerate(camera_list['camera_list']):
                    if item['dot_id'] == str(zset):
                        dn_rtsp = item["dn_rtsp"]
                        camera_rtsp = item["source_rtsp"]
                        dot_id = item["dot_id"]
                        # 启动线程
                        task_id = str(int((int(dot_id) + 2)/3))
                        print("type=", values["type"], "task_id=", task_id, " dot_id =", dot_id)
                        # print("find board in main")
                        # 清除当前球机的标志位
                        self.line[task_id][dot_id] = 0
                        self.find_board(dn_rtsp, camera_rtsp, dot_id, task_id, values["type"])  # 启动找板程序
                        break
        
    
    



get_queue = GetQueue()
get_queue.thread_start()
get_queue.loop_scan()
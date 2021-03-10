import os, time
from threading import Timer
from datetime import datetime


path = "/root/app/logs"


# 清除 days前天的日志 同一个文件
def clear_before_txt(path, days):
    if not os.path.exists(path):
        print("file not found")
        return 
    time_now = time.time() - days * 86400
    time_end = time.strftime("%Y-%m-%d", time.localtime(time_now))
    print(time_end)
    with open(path, "a+", encoding="utf8") as fp:
        fp.seek(0)
        contents = fp.readlines()
        rm_index = -1
        for index,item in enumerate(contents):
            print(item)
            if time_end in item:
                print("ok")
                print(index)
                rm_index = index
                break
        if rm_index != -1:
            fp.truncate(0)
            for item in contents[rm_index:]:
                fp.write(item)


def clear_half_txt(path):
    if not os.path.exists(path):
        print("file not found")
        return 
    with open(path, "a+", encoding="utf8") as fp:
        fp.seek(0)
        contents = fp.readlines()
        # print(contents, len(contents))
        fp.truncate(0)
        contents_len = len(contents)//2
        for item in contents[contents_len:]:
            fp.write(item)

def reboot_program(hours):
    timing = hours * 3600   # 一小时

    now_time = time.localtime(time.time())
    print(now_time)
    # 4点
    clear_hour = 4
    if now_time[3] == clear_hour:
        print(str(clear_hour) + "点")
        os.system("ps -ef | grep -v grep | grep get_queue.py  | awk '{print $2}' | xargs kill")
    
    t = Timer(timing, reboot_program, (hours,))
    t.start()


def clear_file(days, path):
    timing = days * 86400   # 一天

    if not os.path.exists(path):
        print("path not exists")
        t = Timer(timing, clear_file, (days, path,))
        t.start()
        return
    else:
        # # 获取今天是星期几0-6 -> 星期一~日
        # day_of_week = datetime.now().weekday()
        # print(day_of_week)
        # # 星期日固定删除文件
        # if day_of_week == 6:
        logs_list = os.listdir(path)
        for filename in logs_list:
            # print(filename)
            full_name = os.path.join(path, filename)
            # 删除日志
            # cmd = "rm " + full_name
            # os.system(cmd)
            # 删除一半的日志
            # clear_half_txt(full_name)
            clear_before_txt(full_name, 15)

    t = Timer(timing, clear_file, (days, path,))
    t.start()


if __name__ == "__main__":
    clear_file(1, path)
    reboot_program(1)
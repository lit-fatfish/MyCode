import os, time


path = "clear.txt"

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


clear_before_txt(path, 15)
# clear_half_txt(path)
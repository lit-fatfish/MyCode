# 自动获取推理视频和原视频视频中没有转码的视频，加入到转码队列

import os

from extend.redis_tools import RedisTools


## 处理步骤
"""
读取两个视频列表，加入视频的结尾是mp4.mp4说明没有转码，加入到对应的队列
"""

r = RedisTools("172.17.0.1", 6379, "anlly12345", 0)


dst_path = "/home/detection_video"

src_path = "/home/source_video"

dst_lists = os.listdir(dst_path)

print(dst_lists[1])

for dst_index,file_name in enumerate(dst_lists):
    full_path = os.path.join(dst_path, file_name)
    # print(full_path)
    if full_path.endswith('mp4.mp4'):
        print(full_path)
        video_size = os.path.getsize(full_path)
        print(video_size)
        if video_size > 1000 and video_size < 200000000:
            r.write_queue("dst_video_list", full_path)
        if dst_index>5:
            pass
            # break

src_lists = os.listdir(src_path)

for src_index,file_name in enumerate(src_lists):
    full_path = os.path.join(src_path, file_name)
    if full_path.endswith('mp4.mp4'):
        print(full_path)
        video_size = os.path.getsize(full_path)
        # print(video_size)
        if video_size > 1000 and video_size < 200000000:
            r.write_queue("dst_video_list", full_path)
        if src_index>5:
            pass
            # break

print("dst_index", dst_index)

print("src_index", src_index)
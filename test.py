import psutil
import os

##写一个统计文件长度的程序

def get_file_lenght(filepath):
  count = 0
  for index, item in enumerate(open(filepath, "r")):
    count += 1
  return count

print(get_file_lenght("config.json"))

# if not os.path.exists("hello.py"):
#   print("不存在")

# # 测试test_model.py 里面的程序
# def convertBack(x, y, w, h):
#   xmin = int(round(x - (w / 2)))
#   xmax = int(round(x + (w / 2)))
#   ymin = int(round(y - (h / 2)))
#   ymax = int(round(y + (h / 2)))
#   return xmin, ymin, xmax, ymax

# print(convertBack(1,2,3,4))

# import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument('--sparse', action='store_true', default=False, help='GAT with sparse version or not.')
# parser.add_argument('--seed', type=int, default=72, help='Random seed.')
# parser.add_argument('--epochs', type=int, default=10000, help='Number of epochs to train.')

# args = parser.parse_args()

# print(args.sparse)
# print(args.seed)
# exit(0)
# print(args.epochs)

# core_num = psutil.cpu_count()
# print("core_num=", core_num)
# memory = psutil.virtual_memory()
# print("memory=",memory)


# # subprocess 理解
# # subprocess 模块允许我们启动一个新进程，并连接到它们的输入/输出/错误管道，从而获取返回值。
# import subprocess
# def runcmd(command):
#     ret = subprocess.run(command,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,encoding="utf-8",timeout=1)
#     if ret.returncode == 0:
#         print("success:",ret)
#     else:
#         print("error:",ret)
#
#
# runcmd(["dir","/b"])#序列参数
# runcmd("exit 1")#字符串参数

# # file-name:print_name.py
# import argparse
#
#
# def get_parser():
#     parser = argparse.ArgumentParser(description="Demo of argparse")
#     parser.add_argument('--name', default='Great')
#
#     return parser
#
#
# if __name__ == '__main__':
#     parser = get_parser()
#     args = parser.parse_args()  # 通过argpaser对象的parser_args函数来获取所有参数args
#     name = args.name  # 然后通过args.name的方式得到我们设置的--name参数的值
#     print('Hello {}'.format(name))
#
# # python test.py --name DaiDai 输出Hello DaiDai

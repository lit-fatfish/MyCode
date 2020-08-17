import psutil

core_num = psutil.cpu_count()
print("core_num=", core_num)
memory = psutil.virtual_memory()
print("memory=",memory)


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

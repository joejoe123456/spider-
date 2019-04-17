'''
Created on 2018年10月23日

@author: Administrator
'''
import operator


import sys, os
print('--------')
for path in sys.path:
    print(path)
print('--------')

print(os.path.abspath(__file__))  #打印当前文件所处的绝对路径
print(os.path.dirname(os.path.abspath(__file__))) #打印当前文件所处的目录
# 打印当前文件所处的目录的父目录
print( os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)  # 将BASE_DIR加入到系统环境变量
print('--------')
for path in sys.path:
    print(path)
print('--------')
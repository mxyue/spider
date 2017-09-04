# coding:utf-8
import socket

# 链接服务端ip和端口
ip_port = ('192.168.1.38', 9999)
# 生成一个句柄
sk = socket.socket()
# 请求连接服务端
sk.connect(ip_port)
# 发送数据

sk.sendall('f')

server_reply = sk.recv(8)
# 打印接受的数据
print (server_reply)
# 关闭连接
sk.close()

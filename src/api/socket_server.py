# coding:utf-8
import socket

# 开启ip和端口
ip_port = ('0.0.0.0', 9999)
# 生成一个句柄
sk = socket.socket()
# 绑定ip端口
sk.bind(ip_port)
# 最多连接数
sk.listen(5)


def print_content():
    while True:
        print ('server waiting...')
        # 等待链接,阻塞，直到渠道链接 conn打开一个新的对象 专门给当前链接的客户端 addr是ip地址
        conn, addr = sk.accept()
        # 获取客户端请求数据
        client_data = conn.recv(8)
        # 打印对方的数据
        print (client_data)
        # 向对方发送数据
        conn.sendall('1')
        # 关闭链接
        conn.close()


try:
    # 开启死循环
    print_content()
finally:
    print('关闭')
    sk.close()

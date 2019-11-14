import socket
import multiprocessing
import re
import time
from dynamic import mini_frame
import sys
import logging
sys.path.append('G:\pythonproject\miniweb\dynamic')

logging.basicConfig(level=logging.INFO,
                    filename='./logserver.txt',
                    filemode='a',
                    format='%(asctime)s-%(filename)s[line:%(lineno)d]-%(levelname)s:%(message)s'
                    )

class WSGIServer(object):

    def __init__(self,port,app):
        """

        :param port:
        :param app:
        """
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcp_socket.bind(('', port))
        self.tcp_socket.listen(128)

        self.application = app


    def fun_send(self,new_socket):
        """

        :param new_socket:
        """
        # print('新连接')
        read_data = new_socket.recv(1024).decode('utf-8')
        # print(read_data.decode('utf-8'))
        # http的hader和body必须空行分开，在字符串中用\n和、\r
        file_name = re.match(r'[^/]+(/[^ ]*)',read_data)
        # print(file_name.group(1))

        if file_name:
            file_name = file_name.group(1)
            logging.info("recv:%s" % file_name)
            if file_name == '/':
                file_name= '/index.html'

            # 若果不是以。html结尾
            if not file_name.endswith('.html'):
                try:
                    fr = open('./'+file_name,'rb')
                except:
                    body = '<h1> no file'
                    header = "HTTP/1.1 404 notdound\r\n\r\n"
                    send_data = (header + body).encode('gbk')

                else:
                    body = fr.read()
                    header = "HTTP/1.1 200 ok\r\n\r\n"
                    send_data = header.encode('gbk') + body
                    fr.close()
                finally:
                    new_socket.send(send_data)
            else:
                 #     否则为动态资源请求
                env = dict()
                env['PATHINFO'] = file_name
                body = self.application(env,self.set_response)
                header = "HTTP/1.1 %s\n" % self.status
                for a,b in self.header_list:
                    header = header +  a + ':'+ b +'\n'

                header += '\r\n\r\n'
                # print(header)
                # print(type(header), print(type(body)))
                send_data = header.encode('gbk') + body

                new_socket.send(send_data)

        new_socket.close()

    def set_response(self,status,header):
        self.status = status
        self.header_list = [('Server','miniweb1.0')]
        self.header_list += header

    def run_forever(self):

        while True:

            new_socket, clientaddr = self.tcp_socket.accept()
            del_con = multiprocessing.Process(target= self.fun_send,args = (new_socket,))
            del_con.start()
            # 进程复制所以要关闭两次
            new_socket.close()
        # 线程共享socket，只需要关闭一次,进程复制，所以要关闭两次，类似于软硬链接
        self.tcp_socket.close()


def main():

    if len(sys.argv) != 3:
        print(sys.argv)
        print('cmd：python3 7777 miniframe:application')
        return
    ret = re.match(r'([^:]+):(.*)',sys.argv[2])
    if ret:
        framename = ret.group(1)
        appname = ret.group(2)
    else:
        print('check cmd：python3 7777 miniframe:application')
        return

    port = int(sys.argv[1])
    frame = __import__(framename)
    app = getattr(frame,appname)


    wserver=WSGIServer(port,app)
    wserver.run_forever()


if __name__ == '__main__':
    main()





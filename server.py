# -*- coding: utf-8 -*-
"""
Created on Mon Dec 18 15:44:54 2017

@author: Chens
"""


from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
import json
from ocr import OCRNeuralNetwork
import numpy as np
import random

#服务器端配置
HOST_NAME = 'localhost'
PORT_NUMBER = 8000
#这个值是通过运行神经网络设计脚本得到的最优值
HIDDEN_NODE_COUNT = 20

# 加载数据集
data_matrix = np.loadtxt(open('data.csv', 'rb'), delimiter = ',')
data_labels = np.loadtxt(open('dataLabels.csv', 'rb'))

# 转换成list类型
data_matrix = data_matrix.tolist()
data_labels = data_labels.tolist()

# 数据集一共5000个数据，train_indice存储用来训练的数据的序号
train_indice = list(range(5000))
# 打乱训练顺序
random.shuffle(train_indice)

nn = OCRNeuralNetwork(HIDDEN_NODE_COUNT, data_matrix, data_labels, train_indice);

class JSONHandler(SimpleHTTPRequestHandler):
    """处理接收到的POST请求"""
    def do_POST(self):
        response_code = 200
        response = ""
        var_len = int(self.headers.get('Content-Length'))
        content = self.rfile.read(var_len);
        payload = json.loads(content);

        # 如果是训练请求，训练然后保存训练完的神经网络
        if payload.get('train'):
            nn.train(payload['trainArray'])
            nn.save()
        # 如果是预测请求，返回预测值
        elif payload.get('predict'):
            try:
                print(nn.predict(data_matrix[0]))
                response = {"type":"test", "result":str(nn.predict(payload['image']))}
            except:
                response_code = 500
        else:
            response_code = 400

        self.send_response(response_code)
        self.send_header("Content-type".encode(), "application/json".encode())
        self.send_header("Access-Control-Allow-Origin".encode(), "*".encode())
        self.end_headers()
        if response:
            self.wfile.write(bytes(json.dumps(response), 'utf-8'))
        return

if __name__ == '__main__':
    server_class = HTTPServer;
    httpd = server_class((HOST_NAME, PORT_NUMBER), JSONHandler)

    try:
        #启动服务器
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    else:
        print("Unexpected server exception occurred.")
    finally:
        httpd.server_close()

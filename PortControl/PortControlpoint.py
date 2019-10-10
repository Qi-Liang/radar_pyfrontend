import os
import os.path
import copy
import time
import logging
import serial
import _thread
import threading
import binascii
from ctypes import *
import matplotlib.pyplot as plt
import math
import datetime
import json
from mpl_toolkits.mplot3d import Axes3D

from collections import OrderedDict


data_port = serial.Serial()
user_port = serial.Serial()
data_buffer = []
dataReceiveThread = ""
HEADER_SIZE = 52
SINGLE_POINT_DATA_SIZE = 20
# Process height at frontend
HEIGHT_RANGE = 0.4
RADAR_HEIGHT = 1.6
NOMAL_FACTOR = 0.02
point_data = {"range":0.0, "azimuth":0.0, "elev":0.0, "doppler":0.0, "snr":0.0}
point_data1 = {"x":0.0, "y":0.0, "z":0.0}


def open_port():
    try:
        data_port.port = 'COM6'  # 端口号
        data_port.baudrate = 921600  # 波特率
        data_port.bytesize = 8  # 数据位
        data_port.stopbits = 1  # 停止位
        data_port.parity = "N"  # 校验位
        data_port.open()
        if data_port.isOpen():
            print("打开成功")
        else:
            print("打开失败")

        # global dataReceiveThread
        # dataReceiveThread = threading.Thread(target=data_receive_function, args=())
        # dataReceiveThread.start()

        user_port.port = "COM7"  # 端口号
        user_port.baudrate = 115200  # 波特率
        user_port.bytesize = 8  # 数据位
        user_port.stopbits = 1  # 停止位
        user_port.parity = "N"  # 校验位
        user_port.open()
        if user_port.isOpen():
            print("打开成功")
        else:
            print("打开失败")
        # _thread.start_new_thread(init_board, ())

        init_board()
        # data_receive_function()
        _thread.start_new_thread(data_receive_function(), ())

    except Exception as ex:
        print(ex)


def init_board():
    current_dir = os.path.dirname(__file__)
    file = open(current_dir + "/mmw_pplcount_demo_default.cfg", "r+")
    if file is None:
        print("配置文件不存在!")
        return
    for text in file.readlines():
        print("send config:" + text)

        user_port.write(text.encode('utf-8'))
        user_port.write('\n'.encode('utf-8'))
        time.sleep(0.2)
    file.close()


def data_receive_function():
    ponit_data_list_list = []  # 该列表用来存放点数据
    time2 = datetime.datetime.now()
    count = 0
    hello = OrderedDict()
    while 1:
        if data_port is not None and data_port.isOpen():
            try:
                if data_port.in_waiting:
                    buffer = str(binascii.b2a_hex(data_port.read(data_port.in_waiting)))[2:-1]
                    valid_data = []
                    for i in range(len(buffer)):
                        valid_data.append((buffer[i]))
                    # print(valid_data)
                    data_buffer.extend(valid_data)
                    point_data = process_data()
                    print(point_data)
                    ponit_data_list_list.extend(point_data)
                    time1 = datetime.datetime.now()

                    count += 1
                    # print(type(ponit_data_list_list))


                    if ponit_data_list_list:
                        print(ponit_data_list_list)


                        hello.update({count: point_data})
                        # print(ponit_data_list_list)
                        xs, ys, zs = [], [], []
                        # for ponit_data in ponit_data_list_list:
                        for data in point_data:
                           xs.append(data['x'])
                           ys.append(data['y'])
                           zs.append(data['z'])
                            # point_data.insert(0,count)

                        print('1111',time1.second,'222' , time2.second)
                        # if abs(time1.second - time2.second) >= 1 and xs:
                        if xs:
                            fig = plt.figure()
                            ax = fig.add_subplot(111, projection='3d')

                            print('3333', xs)
                            ax.scatter(xs, ys, zs, c = 'r', marker = 'o')
                            time2 = datetime.datetime.now()

                            ax.set_xlabel('X Label' + ' Frame' + str(count))
                            ax.set_ylabel('Y Label')
                            ax.set_zlabel('Z Label')
                            plt.show()
                            plt.pause(0.001)
                            plt.close()
                        # print("here" ,hello)
                with open('hi.json', 'w') as f:
                    # f.write(str(hello))
                    json.dump(hello, f)

            except TimeoutError:
                print('Time Out Error')
            except Exception as ex:
                print("EXCEPTION:", ex.__traceback__)
                print("EXCEPTION_detail:", ex)
        time.sleep(0.01)


def process_data():

    while len(data_buffer) >= HEADER_SIZE:
        frame_data = get_frame()
        if frame_data is None:
            return
        # (frame_data)

        if len(frame_data) == HEADER_SIZE*2:
            print("空数据帧！")
            continue
# "fdfadsfasdf23434tgsfdgsfd"
# "point_head [point_cloud_head + points]"

        index = HEADER_SIZE * 2
        # Split point cloud data and human data
        # Get point cloud data
        tlv_type = int(convert_string("".join(frame_data[index:index + 8])), 16)
        index += 8
        point_cloud_len = int(convert_string("".join(frame_data[index:index + 8])), 16)
        index += 8
        point_num = int(point_cloud_len / SINGLE_POINT_DATA_SIZE)
        if tlv_type == 6:
            print("Point cloud: Exists " + str(point_num) + " points")
        else:
            print("TLV type: " + str(tlv_type))

        point_data_list = [copy.deepcopy(point_data) for i in range(point_num)]
        point_data_list1 = [copy.deepcopy(point_data1) for i in range(point_num)]
        for i in range(point_num):
            r = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            point_data_list[i]["range"] = r
            index += 8
            fi = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            point_data_list[i]["azimuth"] = fi
            index += 8
            thita= byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            point_data_list[i]["elev"] = thita
            index += 8
            point_data_list[i]["doppler"] = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            point_data_list[i]["snr"] = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            xs = r * math.cos(thita)* math.sin(fi)
            ys = r * math.cos(thita)* math.cos(fi)
            zs = r * math.sin(thita)
            point_data_list1[i]["x"] = xs
            point_data_list1[i]["y"] = ys
            point_data_list1[i]["z"] = zs
        # TODO: Stop printing out points.
        return point_data_list1


def get_frame():
    data_str = "".join(data_buffer)
    # print("data_str:" + data_str)
    start_index = data_str.index("0201040306050807")
    if start_index == -1:
        return None
    start_index = int(start_index)
    del data_buffer[0:start_index]
    start_index = 0
    if len(data_buffer) < HEADER_SIZE:
        return None
    packet_len = int(convert_string("".join(data_buffer[start_index + 40:start_index + 48])), 16)
    print("数据包大小:" + str(packet_len))
    if packet_len > 30000:
        print("数据包大小超过30000，丢弃帧")
        del data_buffer[0:24]
        return None
    if len(data_buffer) < packet_len:
        return None
    ret = copy.deepcopy(data_buffer[start_index: start_index + packet_len * 2])
    del data_buffer[start_index: start_index + packet_len * 2]

    return ret


def on_application_quit():
    try:
        if data_port is not None:
            user_port.close()
        if data_port is not None:
            data_port.close()
    except Exception as ex:
        print(ex.__context__)


def convert_string(string):
    try:
        # str1 = string[2:4] + string[0:2] + string[6:8] + string[4:6]
        str1 = string[6:8] + string[4:6] + string[2:4] + string[0:2]
        return str1
    except IndexError as idxerr:
        print(idxerr.__context__)


def byte_to_float(s):
    i = int(s, 16)
    cp = pointer(c_int(i))
    fp = cast(cp, POINTER(c_float))
    return fp.contents.value


if __name__ == '__main__':
    open_port()

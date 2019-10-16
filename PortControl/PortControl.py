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
import math
import datetime
import json

from collections import OrderedDict

data_port = serial.Serial()
user_port = serial.Serial()
data_buffer = []
dataReceiveThread = ""
HEADER_SIZE = 52

# Process height at frontend
POSTURES = {0: "UNKNOWN", 1: "STANCE", 2: "SITTING", 3: "LYING"}
HEIGHT_MESURE_TIMES = 150
CFAR_REMOVAL_THRE = 40
SINGLE_HUMAN_DATA_SIZE = 36
height_map = dict()
count_map = dict()
tid_set = set()
human_data_map = dict()
human_data = {"tid": 0, "pos_x": 0.0, "pos_y": 0.0, "pos_z": 0.0, "vel_x": 0.0, "vel_y": 0.0, "vel_z": 0.0 , "man_height": 0.0, "posture_state": 0}
HEIGHT_RANGE = 0.4
RADAR_HEIGHT = 1.6
NOMAL_FACTOR = 0.02

# Point data
SINGLE_POINT_DATA_SIZE = 20
point_data = {"range":0.0, "azimuth":0.0, "elev":0.0, "doppler":0.0, "snr":0.0}
point_data1 = {"x":0.0, "y":0.0, "z":0.0}

time_start_flag = False
time_end_flag = False
time_start = 0
time_end = 0



# Calculate height by updating tidSet and maps
def cal_height(tid, pos_z):
    if pos_z <= 0.3 or pos_z > 2.5:
        return
    tid_set.add(tid)

    if count_map.__contains__(tid):
        if count_map[tid] <= HEIGHT_MESURE_TIMES:
            count_map[tid] += 1
            if pos_z > RADAR_HEIGHT + HEIGHT_RANGE or pos_z < RADAR_HEIGHT - HEIGHT_RANGE:
                height_map[tid] = (1.0 - NOMAL_FACTOR) * height_map[tid] + NOMAL_FACTOR * pos_z
            else:
                height_map[tid] = 0.95 * height_map[tid] + 0.05 * pos_z
    else:
        count_map[tid] = 1
        height_map[tid] = 0.8 * RADAR_HEIGHT + 0.2 * pos_z
        height_map[tid] = 1.3 * height_map[tid]


def remove_unused_tid():
    if count_map.__len__() > 0:
        for tid in count_map.keys():
            if not tid_set.__contains__(tid):
                count_map.pop(tid)
                height_map.pop(tid)

def judge_posture(height_rate):
    posture_state = 0
    if height_rate > 0.75:
        posture_state = 1
    elif height_rate > 0.35:
        posture_state = 2
    elif posture_state > 0.1:
        posture_state = 3
    return posture_state


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

        user_port.port = "COM5"  # 端口号
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
    global time_start
    global time_start_flag
    current_dir = os.path.dirname(__file__)
    file = open(current_dir + "/mmw_pplcount_demo_default.cfg", "r+")
    if file is None:
        print("配置文件不存在!")
        return
    for text in file.readlines():

        if text == "sensorStart":
            if time_start_flag is False:
                time_start = time.time()
                time_start_flag = True
        print("send config:" + text)

        user_port.write(text.encode('utf-8'))
        user_port.write('\n'.encode('utf-8'))
        time.sleep(0.2)
    file.close()


def data_receive_function():
    ponit_data_list_list = []  # 该列表用来存放点数据
    count = 0
    pointCloudJson = OrderedDict()
    humanJson = OrderedDict()

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
                    count += 1

                    if point_data:
                        # Update point cloud file
                        pointCloudJson.update({count: point_data})
                        humanJson.update({count: human_data_map})
                        # Set initial two point to fix the border.
                        xs, ys, zs = [5, -5], [0, 6], [5, -5]
                        hxs, hys, hzs = [], [], []
                        for data in point_data:
                           xs.append(data['x'])
                           ys.append(data['y'])
                           zs.append(data['z'])
                        for tid in tid_set:
                            hxs.append(human_data_map[tid]['pos_x'])
                            hys.append(human_data_map[tid]['pos_y'])
                            hzs.append(human_data_map[tid]['pos_z'])

                        # TODO: Use pyqtgraph to show points in real time









                # Store points and human info in json file
                with open('../Data/PointCloud.json', 'w') as f:
                    # f.write(str(pointCloudJson))
                    json.dump(pointCloudJson, f)

                with open('../Data/HumanInfo.json', 'w') as f:
                    json.dump(humanJson, f)
            except TimeoutError:
                print('Time Out Error')
            except Exception as ex:
                print("EXCEPTION:", ex.__traceback__)
                print("EXCEPTION_detail:", ex)
        time.sleep(0.01)


def process_data():
    # Refresh tidSet
    tid_set.clear()
    global time_end
    global time_start
    global time_end_flag

    while len(data_buffer) >= HEADER_SIZE:
        posture_count = {x: 0 for x in POSTURES.values()}

        frame_data = get_frame()
        if frame_data is None:
            return
        # (frame_data)

        if len(frame_data) == HEADER_SIZE*2:
            print("空数据帧！")
            continue


        index = HEADER_SIZE * 2
        # Split point cloud data and human data
        # Get point cloud data
        tlv_type = int(convert_string("".join(frame_data[index:index + 8])), 16)
        index += 8
        point_cloud_len = int(convert_string("".join(frame_data[index:index + 8])), 16)
        index += 8
        point_num = int(point_cloud_len / SINGLE_POINT_DATA_SIZE)

        with open('time_lab.txt', 'a+') as f:
            f.write(str(time.time()) + " ===> " + str(point_num) + "\n")


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
        # Get human clusters
        if index == len(frame_data):
            return point_data_list1
        else:
            if time_end_flag is False:
                time_end = time.time()
                time_end_flag = True
                time_duration = time_end-time_start
                with open('time_lab.txt', 'a+') as f:
                    f.write("Time of human being detected : " + str(time_duration) + "\n")
            print("检测到人")
        tlv_type = int(convert_string("".join(frame_data[index:index + 8])), 16)
        index += 8
        content_length = int(convert_string("".join(frame_data[index:index + 8])), 16) - 8
        print(content_length)
        index += 8
        if content_length % SINGLE_HUMAN_DATA_SIZE != 0:
            print("人数据长度错误!")
            continue
        human_count = content_length / SINGLE_HUMAN_DATA_SIZE
        human_count = int(human_count)
        print("传递聚类数：" + str(human_count))

        human_data.clear()
        for i in range(human_count):
            # tid = int.from_bytes(bytearray(frame_data[index:index + 4]), signed=False)
            tid = int(convert_string("".join(frame_data[index:index + 8])), 16)
            index += 8
            pos_x = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            pos_y = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            pos_z = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            vel_x = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            vel_y = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            vel_z = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            man_height = byte_to_float(convert_string("".join(frame_data[index:index + 8])))
            index += 8
            posture_state = int(convert_string("".join(frame_data[index:index + 8])), 16)
            index += 8

            human_data_map[tid] = human_data.copy()
            human_data_map[tid]["tid"] = tid
            human_data_map[tid]["pos_x"] = pos_x
            human_data_map[tid]["pos_y"] = pos_y
            human_data_map[tid]["pos_z"] = pos_z
            human_data_map[tid]["vel_x"] = vel_x
            human_data_map[tid]["vel_y"] = vel_y
            human_data_map[tid]["vel_z"] = vel_z
            human_data_map[tid]["man_height"] = man_height
            human_data_map[tid]["posture_state"] = posture_state

            cal_height(tid, pos_z)
            if int(count_map.get(tid)) <= CFAR_REMOVAL_THRE:
                human_count -= 1
                continue

            man_height = height_map[tid]
            posture_state = judge_posture(float(pos_z) / man_height)
            human_data_map[tid]["posture_state"] = posture_state
            posture_count[POSTURES[posture_state]] += 1

        remove_unused_tid()
        print("检测到的人数：" + str(human_count))
        for tmp_id in count_map.keys():
            print("| ID: " + str(tmp_id))
            print("|- Info: Height = " + str(height_map[tmp_id]) + " Posture = " + POSTURES[
                human_data_map[tid]["posture_state"]])
            print("|- Count: " + str(count_map[int(tmp_id)]))
        print("各类姿态人数：")
        for posture_name in POSTURES.values():
            print("--" + posture_name + ": " + str(posture_count[posture_name]))
        print("------------------------------")
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

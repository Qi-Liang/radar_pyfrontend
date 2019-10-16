# 作者     ：gw
# 创建日期 ：2019-10-15  下午 15:35
# 文件名   ：FrameShow.py


from PyQt5.Qt import *
import sys
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl
import json
from PyQt5.QtCore import QTimer
import re

# import pyqtgraph.examples
# pyqtgraph.examples.run()

# 正则表达式匹配数字
raw_str = '32fdsfa42'
pattern = re.compile(r"\d+\.?\d*")
# print(pattern.search(raw_str)[0])

def Singleton(cls):
    '''
    单例模式
    :param cls:
    :return:
    '''
    _instance = {}
    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]
    return _singleton


def OnlyTime(func):
    '''
    保证函数只执行一次（防止函数重复调用）
    :param func:
    :return:
    '''
    onlyOne = True
    cls = {}
    def inner(*args, **kwargs):
        nonlocal onlyOne
        if onlyOne:
            onlyOne = False
            return func(*args, **kwargs)
    return inner

index = 0


class ListWidget(QListWidget):
    def clicked(self, index):
        # QMessageBox.information(self, "Frame", "Choice:" + index.text())
        print(index.text())
        frame_index = pattern.search(index.text())[0]
        print(frame_index)
        window.frame_now_num.setText("第" + str(frame_index) + "帧")
        window.scater_plt_3d.setData(pos=window.res_[int(frame_index)-1])

@Singleton
class Window(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("FrameShow")
        self.resize(500, 500)
        self.res = []
        self.set_ui()
        # self.data_test_2d()
        self.data_test_3d()
        self.x_data = []
        self.y_data = []
        self.z_data = []
        # self.process_static_data()
        # self.set_timer()
        self.bind_func()

    def set_ui(self):
        self.previous_frame_btn = QPushButton("上一帧", self)
        self.next_frame_btn = QPushButton("下一帧", self)
        self.play_btn = QPushButton("播放", self)
        self.stop_btn = QPushButton("暂停", self)
        self.frame_list_choice = ListWidget(self)
        self.frame_list_choice.adjustSize()
        self.people_num_txt = QLabel(self)
        self.frame_now_num = QLabel(self)
        self.jump_to_frame_label = QLabel("跳跃到第几帧：", self)

        self.people_num_txt.setText("people_num : "+"3")
        # self.plt_2d = pg.PlotWidget()
        # 二维图像

        self.plt_3d = gl.GLViewWidget()

        layout = QGridLayout()
        layout.addWidget(self.people_num_txt, 0, 0, 1, 1)
        layout.addWidget(self.frame_now_num, 1, 0)
        layout.addWidget(self.jump_to_frame_label, 2, 0)
        layout.addWidget(self.frame_list_choice, 3, 0)
        layout.addWidget(self.previous_frame_btn, 4, 0)
        layout.addWidget(self.next_frame_btn, 4, 1)
        layout.addWidget(self.play_btn, 4, 2)
        layout.addWidget(self.stop_btn, 4, 3)
        # layout.addWidget(self.plt_2d, 0, 1, 4, 3)
        layout.addWidget(self.plt_3d, 0, 1, 4, 3)
        self.setLayout(layout)


    def data_test_2d(self):
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)
        self.plt.plot(x, y, pen=None, symbol='o')

    def data_test_3d(self):
        x = gl.GLGridItem()
        y = gl.GLGridItem()
        z = gl.GLGridItem()
        '''
        x.rotate(90, 0, 1, 0)
        y.rotate(90, 1, 0, 0)

        x.scale(0.2, 0.1, 0.1)
        y.scale(0.2, 0.1, 0.1)
        z.scale(0.1, 0.2, 0.1)

        self.pos = np.empty((3, 3))
        size = np.empty((3))
        color = np.empty((3, 4))
        self.pos[0] = (3, 0, 0); size[0] = 0.5; color[0] = (1.0, 0.0, 0.0, 0.2)
        self.pos[1] = (0, 3, 0); size[1] = 1; color[1] = (0.0, 0.0, 1.0, 0.5)
        self.pos[2] = (0, 0, 3); size[2] = 2; color[2] = (0.0, 1.0, 0.0, 1)
        '''

        self.process_static_data()
        size = np.random.rand(len(self.res_), 1)
        print(self.res_)
        print(size.shape)
        # print("==============="+str(len(self.res_)))
        self.scater_plt_3d = gl.GLScatterPlotItem(pos=self.res_[0], pxMode=False)
        self.plt_3d.addItem(self.scater_plt_3d)
        self.plt_3d.addItem(x)
        self.plt_3d.addItem(y)
        self.plt_3d.addItem(z)

        self.plt_3d.show()

    @OnlyTime
    def frame_choice(self):
        print("www")
        for i in range(self.data_len):
            self.frame_list_choice.addItem("Frame: 第" + str(i+1) + "帧")

    def process_dynamic_data(self):
        data = {"1": [{"x": 2, "y": 4, "z": 5}, {"x": 3, "y": 4, "z": 2}, {"x": 1, "y": 7, "z": 4}],
                "2": [{"x": 2, "y": 2, "z": 6}, {"x": 3, "y": 4, "z": 8}, {"x": 5, "y": 7, "z": 6}],
                "3": [{"x": 5, "y": 7, "z": 2}, {"x": 1, "y": 5, "z": 6}, {"x": 7, "y": 2, "z": 1}],
                }
        '''
        # 从json文件里面读取数据，并处理成可以合法的数据格式
        if not self.res:
            with open(r'PortControl\hi.json', 'r', encoding='utf-8') as f:
                txt = json.load(f)
                for i in txt:
                    t = []
                    for j in txt[i]:
                        tt = [j['x']*10, j['y']*10, j['z']*10]
                        t.append(tt)
                    self.res.append(t)
            print(self.res)
        '''
        x = gl.GLGridItem()
        y = gl.GLGridItem()
        z = gl.GLGridItem()

        raw_pos = [self.x_data, self.y_data, self.z_data]
        new_pos = np.array(raw_pos).transpose()
        size = np.random.rand(len(new_pos), 1)
        self.scater_plt_3d = gl.GLScatterPlotItem(pos=new_pos, size=size)

        self.plt_3d.addItem(self.scater_plt_3d)
        self.plt_3d.addItem(x)
        self.plt_3d.addItem(y)
        self.plt_3d.addItem(z)
        self.plt_3d.show()

    def process_static_data(self):
        test_data = {"1": [{"x": 2, "y": 4, "z": 5}, {"x": 3, "y": 4, "z": 2}, {"x": 1, "y": 7, "z": 4}],
                "2": [{"x": 2, "y": 2, "z": 6}, {"x": 3, "y": 4, "z": 8}, {"x": 5, "y": 7, "z": 6}],
                "3": [{"x": 5, "y": 7, "z": 2}, {"x": 1, "y": 5, "z": 6}, {"x": 7, "y": 2, "z": 1}],
                }
        '''
        if not self.res:
            with open(r"xxx.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                for i in data:
                    tmp = []
                    for j in data[i]:
                        tmp_ = [j['x']*10, j['y']*10, j['z']*10]
                        tmp.append(tmp_)
                    self.res.append(tmp)
        '''
        if not self.res:
            for i in test_data:
                tmp = []
                for j in test_data[i]:
                    tmp_ = [j['x'], j['y'], j['z']]
                    tmp.append(tmp_)
                self.res.append(tmp)
        self.data_len = len(self.res)
        self.frame_choice()
        self.res_ = np.array(self.res)
        # return self.res, Window.index

    def next_btn(self):
        global index
        self.process_static_data()
        index += 1
        if index == self.data_len:
            index = 0
        size = np.random.rand(len(self.res_), 1)
        self.frame_now_num.setText("第" + str(index+1) + "帧")
        self.scater_plt_3d.setData(pos=self.res_[index], size=size)
        self.frame_list_choice.setCurrentRow(index)
        print(index)


    def previous_btn(self):
        global index
        self.process_static_data()
        index -= 1
        if index == -1:
            index = self.data_len-1
        size = np.random.rand(len(self.res_), 1)
        self.frame_now_num.setText("第" + str(index+1) + "帧")
        self.scater_plt_3d.setData(pos=self.res_[index])
        self.frame_list_choice.setCurrentRow(index)
        print(index)


    def choice_frame(self):
        # self.frame_list_choice.itemClicked.
        pass

    def bind_func(self):
        self.next_frame_btn.pressed.connect(self.next_btn)
        self.previous_frame_btn.pressed.connect(self.previous_btn)
        self.frame_list_choice.itemClicked.connect(self.frame_list_choice.clicked)

    def update_data(self):
        raw_pos = [self.plt_3d, self.y_data, self.z_data]
        new_pos = np.array(raw_pos).transpose()
        size = np.random.rand(len(new_pos), 1)
        self.scater_plt_3d.setData(pos=new_pos, size=size)

    def set_timer(self):
        timer = QTimer()
        timer.timeout.connect(self.update_data)
        timer.start(50)
        print("2")





if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    # timer = QTimer()
    # timer.timeout.connect(window.update_data)
    # timer.start(50)
    window.show()
    sys.exit(app.exec_())

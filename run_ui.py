import sys
import random
import numpy as np
import json
# import pyserial

from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from PortControl import PortControlpoint

plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号




class Window(QtWidgets.QDialog):
    index = 0
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure = plt.figure()
        self.axes = self.figure.add_subplot(111, projection='3d')
        # We want the axes cleared every time plot() is called
        # self.axes.hold(False)
        self.canvas = FigureCanvas(self.figure)

        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.hide()

        # Just some button
        self.button1 = QtWidgets.QPushButton('上一帧')
        self.button1.clicked.connect(self.up_pic)

        self.button2 = QtWidgets.QPushButton('下一帧')
        self.button2.clicked.connect(self.down_pic)

        self.button3 = QtWidgets.QPushButton('传输配置文件')
        self.button3.clicked.connect(self.send_config)

        self.button4 = QtWidgets.QPushButton('无用')
        self.button4.clicked.connect(self.home)

        # set the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        btnlayout = QtWidgets.QHBoxLayout()
        btnlayout.addWidget(self.button1)
        btnlayout.addWidget(self.button2)
        btnlayout.addWidget(self.button3)
        btnlayout.addWidget(self.button4)
        qw = QtWidgets.QWidget(self)
        qw.setLayout(btnlayout)
        layout.addWidget(qw)

        self.setLayout(layout)
        self.res = []

    def home(self):
        self.toolbar.home()

    def down_pic(self):
        ''' plot some random stuff '''
        tmp, index = self.prvoid_data()
        self.axes.clear()
        # self.axes.plot(data, '*-')
        # self.canvas.draw()
        # for i in range(3):
        # print(tmp[:10])
        for i in range(Window.index+1):
            tmp_re = np.array(tmp[i])
            self.axes.scatter(tmp_re[:, 0], tmp_re[:, 1], tmp_re[:, 2],
                   marker='o', c=self.cValue[i%4],s=8, label='class ' + str(Window.index))
        Window.index = (Window.index+1)
        if Window.index == self.n:
            Window.index = 0
        # plt.text(1,2,1, ha='center', va='center')
        self.axes.set_xlabel('X 轴')
        self.axes.set_ylabel('Y 轴')
        self.axes.set_zlabel('Z 轴')
        self.canvas.draw()
        print(Window.index)

    def send_config(self):
        PortControlpoint.open_port()
        # print("f")

    def prvoid_data(self):
        data = {"1": [{"x": 2, "y": 4, "z": 5}, {"x": 3, "y": 4, "z": 2}, {"x": 1, "y": 7, "z": 4}],
                "2": [{"x": 2, "y": 2, "z": 6}, {"x": 3, "y": 4, "z": 8}, {"x": 5, "y": 7, "z": 6}],
                "3": [{"x": 5, "y": 7, "z": 2}, {"x": 1, "y": 5, "z": 6}, {"x": 7, "y": 2, "z": 1}],
                }

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
        self.cValue = ['r','y','g','b']
        self.n = len(self.res)
        print(self.n,"fffffffffffffff")
        tmp = np.array(self.res)
        return tmp, Window.index

    def randomcolor(self):
        colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0, 14)]
        return "#" + color

    def up_pic(self):
        ''' plot some random stuff '''
        tmp, index = self.prvoid_data()
        self.axes.clear()

        # self.axes.plot(data, '*-')
        # self.canvas.draw()
        for i in range(Window.index+1):
            tmp_re = np.array(tmp[i])
            self.axes.scatter(tmp_re[:, 0], tmp_re[:, 1], tmp_re[:, 2],
                       marker='o', c=self.cValue[i%4],s=8, label='class ' + str(Window.index))
        Window.index = Window.index-1
        if Window.index == -1:
            Window.index = self.n-1

        self.axes.set_xlabel('X 轴')
        self.axes.set_ylabel('Y 轴')
        self.axes.set_zlabel('Z 轴')
        self.canvas.draw()
        print(Window.index)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    main = Window()
    main.setWindowTitle('帧展示')
    main.show()
    sys.exit(app.exec_())
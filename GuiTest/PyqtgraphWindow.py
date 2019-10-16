# 作者     ：gw
# 创建日期 ：2019-10-11  下午 20:47
# 文件名   ：gui测试1.py


import pyqtgraph as pg
import time
from PyQt5.Qt import *
import sys
import numpy as np

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("点云展示")
        self.resize(1200, 600)
        self.set_ui()

    def set_ui(self):
        text = QLineEdit("输入帧数")
        self.listw = QListWidget()
        self.plt3D = pg.PlotWidget()
        self.plt2D = pg.PlotWidget()
        # 将绘图窗口加塞到主Window里面去

        # plot2 = pg.plot()
        # 单独展示一个widget绘图窗口

        layout = QGridLayout()
        # 参数列表依次代表：控件名、行、列、占用行数=1、占用列数=1、对齐方式（默认0）。
        layout.addWidget(text,1,0)
        layout.addWidget(self.listw,2,0)
        layout.addWidget(self.plt3D,0,1,3,1)
        layout.addWidget(self.plt2D,0,2,3,1)
        # 参数列表依次代表：控件名、行、列、占用行数、占用列数、对齐方式（默认0）。
        self.setLayout(layout)

    def update_point_cloud(self, xs, ys, zs):
        self.plt2D.plot(xs, ys, pen = 'r', symbol = 'o')
        self.plt3D.plot(xs, ys, zs, pen = 'r', symbol = 'o')

    def update_human_info(self, xs, ys, zs):
        self.plt2D.plot(xs, ys, pen = 'b', symbol = 'o')
        self.plt3D.plot(xs, ys, zs, pen = 'b', symbol = 'o')

    def update_tips_list(self, data):
        self.listw.addItem(data)

    def unit_test(self):
        for i in range(100):
            self.update_tips_list("Frame" + str(i))

            xs = np.random.normal(size=100)
            ys = np.random.normal(size=100)
            zs = np.random.normal(size=100)
            self.update_point_cloud(xs, ys, zs)

            xs = np.random.normal(size=5)
            ys = np.random.normal(size=5)
            zs = np.random.normal(size=5)
            self.update_human_info(xs, ys, zs)

            self.show()
            time.sleep(0.1)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.unit_test()
    sys.exit(app.exec_())
    

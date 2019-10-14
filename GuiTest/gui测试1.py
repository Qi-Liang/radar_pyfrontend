# 作者     ：gw
# 创建日期 ：2019-10-11  下午 20:47
# 文件名   ：gui测试1.py


import pyqtgraph as pg
from PyQt5.Qt import *
import sys
import numpy as np

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("gui测试1")
        self.resize(500, 500)
        self.set_ui()
        self.test_data()

    def set_ui(self):
        btn = QPushButton("点我")
        text = QLineEdit("我是文本内容")
        listw = QListWidget()
        self.plt = pg.PlotWidget()
        # 将绘图窗口加塞到主Window里面去

        # plot2 = pg.plot()
        # 单独展示一个widget绘图窗口

        layout = QGridLayout()
        layout.addWidget(btn,0,0)
        # 参数列表依次代表：控件名、行、列、占用行数=1、占用列数=1、对齐方式（默认0）。
        layout.addWidget(text,1,0)
        layout.addWidget(listw,2,0)
        layout.addWidget(self.plt,0,1,3,1)
        # 参数列表依次代表：控件名、行、列、占用行数、占用列数、对齐方式（默认0）。
        # layout.addWidget(plot2)

        self.setLayout(layout)

    def test_data(self):
        x = np.random.normal(size=1000)
        y = np.random.normal(size=1000)
        self.plt.plot(x, y, pen=None, symbol='o')



if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())
    

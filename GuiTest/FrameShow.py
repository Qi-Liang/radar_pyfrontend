# 作者     ：gw
# 创建日期 ：2019-10-15  下午 15:35
# 文件名   ：FrameShow.py


from PyQt5.Qt import *
import sys
import pyqtgraph as pg
import numpy as np
import pyqtgraph.opengl as gl

# import pyqtgraph.examples
# pyqtgraph.examples.run()


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FrameShow")
        self.resize(500, 500)
        self.set_ui()
        # self.data_test_2d()
        self.data_test_3d()

    def set_ui(self):
        previous_frame_btn = QPushButton("上一帧", self)
        next_frame_btn = QPushButton("下一帧", self)
        play_btn = QPushButton("播放", self)
        stop_btn = QPushButton("暂停", self)
        gap_time_txt = QLineEdit(self)
        people_num_txt = QLabel(self)
        jump_to_frame_label = QLabel("跳跃到第几帧：", self)
        people_num_txt.setText("people_num : "+"3")
        # self.plt_2d = pg.PlotWidget()
        # 二维图像

        self.plt_3d = gl.GLViewWidget()

        layout = QGridLayout()
        layout.addWidget(people_num_txt, 0, 0, 1, 1)
        layout.addWidget(jump_to_frame_label, 2, 0)
        layout.addWidget(gap_time_txt, 3, 0)
        layout.addWidget(previous_frame_btn, 4, 0)
        layout.addWidget(next_frame_btn, 4, 1)
        layout.addWidget(play_btn, 4, 2)
        layout.addWidget(stop_btn, 4, 3)
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

        # x.rotate(90, 0, 1, 0)
        # y.rotate(90, 1, 0, 0)

        # x.scale(0.2, 0.1, 0.1)
        # y.scale(0.2, 0.1, 0.1)
        # z.scale(0.1, 0.2, 0.1)

        self.pos = np.empty((3, 3))
        size = np.empty((3))
        color = np.empty((3, 4))
        self.pos[0] = (3, 0, 0); size[0] = 0.5; color[0] = (1.0, 0.0, 0.0, 0.2)
        self.pos[1] = (0, 3, 0); size[1] = 1; color[1] = (0.0, 0.0, 1.0, 0.5)
        self.pos[2] = (0, 0, 3); size[2] = 2; color[2] = (0.0, 1.0, 0.0, 1)

        self.scater_plt_3d = gl.GLScatterPlotItem(pos=self.pos, size=size, color=color, pxMode=False)

        self.plt_3d.addItem(self.scater_plt_3d)
        self.plt_3d.addItem(x)
        self.plt_3d.addItem(y)
        self.plt_3d.addItem(z)

        self.plt_3d.show()


    def update_data(self):

        self.pos[2][0] += 1
        self.scater_plt_3d.setData(pos=self.pos)





from PyQt5.QtCore import QTimer
if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Window()
    window.show()
    t = QTimer()
    t.timeout.connect(window.update_data)
    t.start(50)


    sys.exit(app.exec_())

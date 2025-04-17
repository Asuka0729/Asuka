# 在Qwidge中画曲线，需要导入QPainter，QColor，QApplication，QMainWindow，QVBoxLayout，QWidget，uic库。
from PyQt5 import QtWidgets, QtCore
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QColor

from qtpy import uic
from sensor_reader import read_sensor_data  # 导入函数

class PlotWidget(QWidget):
    def __init__(self, data):
        super().__init__()
        self.pixels = self.extract_pixel_data(data)

    def extract_pixel_data(self, data):
        """从接收到的数据中提取像素值"""
        if len(data) < 4 + 3648 * 2 + 2:  # 添加检测确保数据长度足够
            raise ValueError("Received data is too short")
        pixel_data = data[4:-2]  # 除去帧头和帧尾
        pixels = []
        for i in range(0, len(pixel_data), 2):
            high_byte = pixel_data[i]
            low_byte = pixel_data[i + 1]
            pixel_value = (high_byte << 8) | low_byte  # 组合成一个像素值
            pixels.append(pixel_value)
            # print(len(pixels))
        """ 使曲线平滑"""
        for i in range(5, 3640, 1):
            pixels[i] = (pixels[i - 5] + pixels[i - 4] + pixels[i - 3] + pixels[i - 2] + pixels[i - 1] + pixels[i] +
                         pixels[i + 1] + pixels[i + 2] + pixels[i + 3] + pixels[i + 4] + pixels[i + 5]) / 11
        """ 求斜率"""
        xielv = [0] * 3630
        for i in range(1, 3560, 1):
            xielv[i] = (pixels[i + 1] - pixels[i - 1]) / 2

        # 初始化列表来存储所有波谷的起点、顶点和终点
        valleys = []

        # 遍历范围
        for i in range(0, 3560, 1):
            xielv[i] = (xielv[i + 6] + xielv[i + 7] + xielv[i + 8] + xielv[i + 9] +
                        xielv[i] + xielv[i + 1] + xielv[i + 2] + xielv[i + 3] +
                        xielv[i + 4] + xielv[i + 5]) / 10

            # 如果找到第一个小于-0.5的斜率（起点）
            if len(valleys) == 0 or (len(valleys) > 0 and valleys[-1]['end'] is not None):
                if xielv[i] < -0.5:
                    valleys.append({'start': i, 'peak': None, 'end': None})  # 记录起点

            # 找到第一个大于0.4的斜率（顶点）
            if len(valleys) > 0 and valleys[-1]['peak'] is None and xielv[i] > 0.4:
                valleys[-1]['peak'] = i  # 记录顶点

            # 找到第一个小于0.4的斜率（终点）
            if len(valleys) > 0 and valleys[-1]['peak'] is not None and valleys[-1]['end'] is None and xielv[i] < 0.4:
                valleys[-1]['end'] = i  # 记录终点

        # 打印结果

        #算出面积
        for valley in valleys:
            if valley['start'] is not None and valley['peak'] is not None and valley['end'] is not None:
                start = valley['start']
                peak = valley['peak']
                end = valley['end']

                Bl = (pixels[start] + pixels[start - 1] + pixels[start - 2] + pixels[start + 1] + pixels[start + 2]) / 5

                Br = (pixels[end] + pixels[end - 1] + pixels[end - 2] + pixels[end + 1] + pixels[end + 2]) / 5
                # 整个面积
                result_value = (Bl + Br) * (end - start) / 2

                # 面积
                s = 0
                for i in range(start, end, 1):
                    s += pixels[i]

                print(f"波谷 起点: {start}, 顶点: {peak}, 终点: {end}, 计算结果: {result_value},面积: {s}")

        return pixels

    # 画笔
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0))  # 设置画笔颜色

        width = self.width()
        height = self.height()

        start_index = 1000
        end_index = 2500

        if end_index > len(self.pixels):
            end_index = len(self.pixels)

        previous_x = None
        previous_y = None

        for index in range(start_index, end_index):
            x = (index - start_index) * (width / (end_index - start_index))
            y = height - (self.pixels[index] / max(self.pixels) * height)

            if previous_x is not None and previous_y is not None:
                painter.drawLine(previous_x, previous_y, int(x), int(y))

            previous_x = int(x)
            previous_y = int(y)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('set_work.ui', self)  # 加载 UI 文件

        # 添加标签引用(寻找标签)
        self.timeLabel = self.findChild(QtWidgets.QLabel, 'timeLabel')  # 寻找时间标签
        self.dateLabel = self.findChild(QtWidgets.QLabel, 'dateLabel')  # 寻找日期标签

        self.pushButton.clicked.connect(self.update_plot)


        # 日期和时间显示
        if self.timeLabel is None:
            print("Error: timeLabel not found in UI")
        if self.dateLabel is None:
            print("Error: dateLabel not found in UI")
        # 创建定时器，每秒更新时间和日期
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # 每1秒触发一次
        # 初始化时间和日期显示
        self.update_time()

    def update_time(self):
        # 获取当前时间和日期
        current_time = QtCore.QTime.currentTime().toString("hh:mm:ss")
        current_date = QtCore.QDate.currentDate().toString("yyyy-MM-dd")

        # 设置时间和日期到标签
        if self.timeLabel and self.dateLabel:
            self.timeLabel.setText(current_time)
            self.dateLabel.setText(current_date)


    def update_plot(self):
        # todo 测试串口并获取数据
        print("打开串口")
        # 调用函数并获取 input_data
        data_string = read_sensor_data()

        # 输出获取的传感器数据
        if data_string is not None:
            print(data_string)
        else:
            print("获取传感器数据失败。")

        byte_list = data_string.split()  # 将字符串拆分为字节列表
        formatted_sequence = ""  # 使用循环构建格式化的字符串

        for byte in byte_list:
            formatted_sequence += f'0x{byte},'  # 在每个字节后加上逗号和空格
        formatted_sequence = formatted_sequence.rstrip(', ')  # 删除最后多余的逗号和空格
        received_data = ([formatted_sequence])




        # 创建 PlotWidget 并添加到 UI 文件中的预留区域
        self.plot_widget = PlotWidget(received_data)

        self.plot_widget = PlotWidget(received_data)
        layout = QVBoxLayout(self.widget)  # 使用 plot_area 的布局
        layout.addWidget(self.plot_widget)
        self.widget.setLayout(layout)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
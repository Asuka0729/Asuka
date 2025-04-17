import sys
from PyQt5 import QtWidgets, QtCore
from qtpy import uic

from main_ui import Ui_Form  # 用你的 UI 文件替代
from sensor_reader import read_sensor_data  # 导入函数
from 画曲线 import MainWindow as CurveWindow  # 导入画曲线的窗口类
from 检测历史 import Ui_Form as HistoryUI
from 批量测试 import Ui_Form as BatchUI


# 主菜单
class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainMenu, self).__init__()
        # 加载主菜单UI文件
        self.ui = Ui_Form()  # 创建 Ui_Form 对象
        self.ui.setupUi(self)  # 将 UI 设置到主窗口

        # 添加标签引用(寻找标签)
        self.timeLabel = self.findChild(QtWidgets.QLabel, 'timeLabel')  # 寻找时间标签
        self.dateLabel = self.findChild(QtWidgets.QLabel, 'dateLabel')  # 寻找日期标签

        self.test = self.findChild(QtWidgets.QFrame, 'test')  # 找到显示测试图标的 QFrame
        self.batch = self.findChild(QtWidgets.QFrame, 'batch')
        self.set_window = self.findChild(QtWidgets.QFrame, 'setup')
        self.history_frame = self.findChild(QtWidgets.QFrame, 'history')  # 新增
        self.batch_test_frame = self.findChild(QtWidgets.QFrame, 'batch_test')  # 新增

        # 连接鼠标点击事件
        # 打开设置界面
        if self.set_window is not None:
            self.set_window.mousePressEvent = self.open_test_ui  # 连接鼠标点击事件
        else:
            print("没有找到设置界面")

        # 串口操作代码
        if self.batch is not None:
            self.batch.mousePressEvent = self.serial_port  # 连接鼠标点击事件

        # 添加曲线按钮点击事件
        if self.test is not None:
            self.test.mousePressEvent = self.open_curve_window  # 连接鼠标点击事件
        else:
            print("没有找到测试按钮")
        # 绑定点击事件
        if self.history_frame:
                self.history_frame.mousePressEvent = self.open_history_ui
        else:
                print("未找到检测历史按钮")

        if self.batch_test_frame:
                self.batch_test_frame.mousePressEvent = self.open_batch_ui
        else:
                print("未找到批量测试按钮")

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

        # 创建并显示test.ui界面
    def open_test_ui(self, event):

        self.test_window = SETWindow()
        # 关闭当前窗口
        self.close()
        # 显示新的窗口
        self.test_window.show()

    def open_curve_window(self, event):
        # 创建并显示曲线窗口
        self.curve_window = CurveWindow()
        # 关闭当前窗口
        self.close()
        # 显示新的窗口
        self.curve_window.show()

    def open_history_ui(self, event):
        # 创建历史记录窗口
        self.history_window = HistoryWindow()
        self.close()  # 关闭当前窗口
        self.history_window.show()

    def open_batch_ui(self, event):
        # 创建批量测试窗口
        self.batch_window = BatchWindow()
        self.close()  # 关闭当前窗口
        self.batch_window.show()

    def serial_port(self, event):
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

        # todo 处理接收到的数据



# 设置界面
class SETWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(SETWindow, self).__init__()
        # 加载test UI文件
        uic.loadUi('./set.ui', self)

        self.timeLabel = self.findChild(QtWidgets.QLabel, 'timeLabel')  # 寻找时间标签
        self.dateLabel = self.findChild(QtWidgets.QLabel, 'dateLabel')  # 寻找日期标签

        # 检查标签是否成功找到
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
        if self.timeLabel and self.dateLabel:  # 确保标签存在
            self.timeLabel.setText(current_time)
            self.dateLabel.setText(current_date)
# 检测历史窗口
class HistoryWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(HistoryWindow, self).__init__()
        self.ui = HistoryUI()  # 使用导入的 HistoryUI 类
        self.ui.setupUi(self)

        # 初始化时间和日期
        self.timeLabel = self.findChild(QtWidgets.QLabel, 'timeLabel')
        self.dateLabel = self.findChild(QtWidgets.QLabel, 'dateLabel')
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        self.update_time()

    def update_time(self):
        current_time = QtCore.QTime.currentTime().toString("hh:mm:ss")
        current_date = QtCore.QDate.currentDate().toString("yyyy-MM-dd")
        if self.timeLabel and self.dateLabel:
            self.timeLabel.setText(current_time)
            self.dateLabel.setText(current_date)



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec_())
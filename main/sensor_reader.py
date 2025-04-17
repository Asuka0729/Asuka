"""
串口读取传感器数据
----------------------------------------------------------
使用方法：
from sensor_reader import read_sensor_data  # 导入函数

# 调用函数并获取 input_data
sensor_data = read_sensor_data()

# 输出获取的传感器数据
if sensor_data is not None:
    print(sensor_data)
else:
    print("获取传感器数据失败。")
----------------------------------------------------------

注意：
 串口号需要根据实际情况修改。
 com3 对应 传感器板
 com7 对应 电机控制板

"""

import serial
import time


def read_sensor_data():
    ser = serial.Serial("COM3", 256000, timeout=1)  # 打开串口
    ser2 = serial.Serial("COM7", 115200, timeout=1)  # 打开另一个串口

    if not ser.isOpen() or not ser2.isOpen():
        print("串口打开失败。")
        return None

    time.sleep(1)

    # 电机运动指令
    stop_str = "\x5A\xa5\x01\x01\x03\x0f\xf9\x01\x0d"  # todo 需要修改走到传感器下面 x0f\xf9\位置 x01\前进 x0d校验
    ser2.write(stop_str.encode('utf-8'))

    time.sleep(1)

    # 传感器读数据指令
    ser.write("@c0007#@".encode('utf-8'))
    time.sleep(1)

    ser.write("@c0080#@".encode('utf-8'))
    time.sleep(1)

    com_input = ser.read(8000)  # com_input就是传感器读到的数据
    input_data = ""

    if com_input:  # 如果读取结果非空，处理数据
        byte_input = com_input.split()

        for byte in byte_input:
            input_data += f'0x{byte},'

        input_data = input_data.rstrip(', ')  # 删除最后多余的逗号和空格

    # 电机运动指令 走到终点
    stop_end = "\x5A\xa5\x01\x01\x03\x0f\xf9\x01\x0d"  #\x5A\xa5\x01\x01\x03  这几项和为  104
    ser2.write(stop_end.encode('utf-8'))

    time.sleep(1)

    # 电机运动指令 回到起点
    stop_start = "\x5A\xa5\x01\x01\x03\x0f\xf9\x00\x0c"  #\x5A\xa5\x01\x01\x03\x0f   和为  113
    ser2.write(stop_start.encode('utf-8'))

    ser.close()  # 关闭串口
    ser2.close()  # 关闭另一个串口

    return input_data  # 返回传感器得到的数据

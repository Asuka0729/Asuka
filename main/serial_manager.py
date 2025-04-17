# serial_manager.py
import serial
import ctypes
import time

class SerialPort:
    def __init__(self, port, baudrate=115200, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def open_port(self):
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            if self.ser.isOpen():
                print("打开串口成功。")
                return True
        except Exception as e:
            print(f"打开串口失败: {e}")
        return False

    def send_data(self, data):
        wbuf = ctypes.create_string_buffer(len(data))
        for i, byte in enumerate(data):
            wbuf[i] = byte
        write_len = self.ser.write(wbuf)
        print("串口发出{}个字节。".format(write_len))
        return write_len

    def read_data(self, size):
        com_input = self.ser.read(size)
        if com_input:
            print("接收到数据:", com_input)
            return com_input
        return None

    def close_port(self):
        if self.ser and self.ser.isOpen():
            self.ser.close()
            print("串口已关闭。")

import serial
import time

def calculate_crc(data):
    """
    计算 CRC-16 (Modbus RTU) 校验码。

    Args:
        data (bytes): 要计算 CRC 的数据。

    Returns:
        int: CRC-16 值。
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def send_data(ser,data_to_send):
    # 计算 CRC
    crc_value = calculate_crc(data_to_send)

    # 添加 CRC 到数据中
    data_with_crc = data_to_send + crc_value.to_bytes(2, byteorder="little")

    # print(data_with_crc.hex().upper())

    # 发送数据
    ser.write(data_with_crc)

def trans_data(speed):
    speed_trans = 2000*speed/100
    hex_number = "{:04x}".format(int(speed_trans)) #:04x控制位数，位数不够自动补0
    return hex_number


if __name__ == "__main__":

    # 配置串口参数
    serial_port = 'COM5'  # 串口号
    baudrate = 9600  # 波特率

    # 创建串口对象
    ser = serial.Serial(port=serial_port, baudrate=baudrate, timeout=3)

    speed = 0

    # 要发送的数据（替换为您的实际数据）
    data_to_send1 = bytes.fromhex("010600000001")  # start
    data_to_send2 = bytes.fromhex("0106000A"+ trans_data(speed))
    data_to_send3 = bytes.fromhex("010600000000")  # stop

    send_data(ser,data_to_send1)
    time.sleep(1)

    while(1):
        print("input speed:")
        speed = input()
        speed = int(speed)
        if speed == 0:
            break
        data_to_send2 = bytes.fromhex("0106000A"+ trans_data(speed))
        send_data(ser,data_to_send2)
        time.sleep(1)
    
    send_data(ser,data_to_send3)


    # 等待一段时间
    time.sleep(1)

    # 关闭串口
    ser.close()
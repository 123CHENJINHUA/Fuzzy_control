import tcp
from com485 import *
from threading import Thread
import multiprocessing
from multiprocessing import Process,Manager

import fuzzy_control2

from queue import Queue

import pandas as pd

import numpy as np

_sentinel = object()

def control_process(plc_test,q_out):

    print("Enter control process---")
    # 配置串口参数
    serial_port = 'COM3'  # 串口号
    baudrate = 9600  # 波特率

    # 创建串口对象
    ser = serial.Serial(port=serial_port, baudrate=baudrate, timeout=3)
    flag = 0
    init_time = 0
    plc_test.send_data(1)

    for num in range(30):
        speed = 0

        # 要发送的数据（替换为您的实际数据）
        data_to_send1 = bytes.fromhex("010600000001")  # start
        data_to_send2 = bytes.fromhex("0106000A"+ trans_data(speed))
        data_to_send3 = bytes.fromhex("010600000000")  # stop

        send_data(ser,data_to_send1)
        time.sleep(1)

        

        receive_list = []

    

        while(1):
            # print("input speed:")
            # speed = input()

            data = q_out.get()

            # if data is _sentinel:
            #     q_out.put(_sentinel)
            #     break

            if plc_test.check_key():
                # q_out.put(_sentinel)
                break

            current_time = data[0]
            if flag == 1:
                init_time = current_time
                flag = 0
            current_time = current_time - init_time
            pressure_value = data[1]
            pressure_rate_value = data[2]
            power = data[3]

            dur_time = 60
            if current_time>(dur_time+1):
                flag=1
                break

            speed = fuzzy_control2.fuzzy_control(pressure_value,pressure_rate_value)
            speed = int(speed)
            # speed = 24
            if speed <24:
                speed = 0
            print("{} at {}".format(speed,current_time))

            receive_list.append([current_time,pressure_value,pressure_rate_value,power,speed])

            # if speed == 0:
            #     break
            data_to_send2 = bytes.fromhex("0106000A"+ trans_data(speed))
            send_data(ser,data_to_send2)
            time.sleep(0.01)

        time.sleep(1)
        
        send_data(ser,data_to_send3)
        print('esc to save the data')

        energy_sum = 0
        
        for i in range(len(receive_list)-1):
            if receive_list[i+1][0]>dur_time:
                break
            energy = np.mean(receive_list[i][3]+receive_list[i+1][3]) * (receive_list[i+1][0]-receive_list[i][0])
            energy_sum += energy

        receive_list.append([energy_sum])
        print("total energy consumption:{} J in {} sec".format(round(energy_sum,2),dur_time))
        # current_time,pressure_value,pressure_rate_value,power,speed
        data_xlsx = pd.DataFrame(receive_list)
        writer = pd.ExcelWriter('./result3/fuzzy/fuzzy_data{}_Eng_{}.xlsx'.format(num,int(energy_sum)))
        data_xlsx.to_excel(writer,sheet_name='page_1')
        writer.close()
        time.sleep(5)

    # 等待一段时间
    time.sleep(1)
    plc_test.send_data(0)
    # 关闭串口
    ser.close()

# class ReceiveProcess(Process):
#     def __init__(self,plc_test):
#         super(ReceiveProcess,self).__init__()
#         self.plc_test = plc_test

#     def run(self):
#         self.plc_test.receive_data()

class ReceiveThread(Thread):
    def __init__(self,plc_test,q_in):
        super(ReceiveThread,self).__init__()
        self.plc_test = plc_test
        self.q_in = q_in

    def run(self):
        self.plc_test.receive_data(self.q_in)

class ControlThread(Thread):
    def __init__(self,plc_test,q_out):
        super(ControlThread,self).__init__()
        self.plc_test = plc_test
        self.q_out = q_out

    def run(self):
        control_process(self.plc_test,self.q_out)

if __name__ == "__main__":

    try:
        
        plc_test = tcp.PC_PLC('192.168.58.20')

        q = Queue()

        thread_data = ReceiveThread(plc_test,q)
        thread_control = ControlThread(plc_test,q)
        thread_data.start()
        thread_control.start()
        thread_data.join()
        thread_control.join()

        # thread_data = Process(target=plc_test.receive_data)
        # thread_control = Process(target=control_process(client_fd))

        # thread_data.start()
        # thread_control.start()

        # thread_data.join()
        # thread_control.join()

        plc_test.close()
    except:
        print ("Error: unable to start thread")
    
        

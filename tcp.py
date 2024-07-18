import struct
import time
import snap7
import keyboard
import pandas as pd

import time
import datetime

from queue import Queue

import numpy as np

_sentinel = object()

class PC_PLC:
	def __init__(self,ip):
		self.ip = ip
		self.client_fd = self.plc_connect(ip, 2)
		print("connect success")


	def plc_connect(self,ip, type, rack=0, slot=1):
		"""
		连接初始化
		:param ip:
		:param type::param connection_type: 1 for PG, 2 for OP, 3 to 10 for S7 Basic
		:param rack: 通常为0	
		:param slot: 根据plc安装，一般为0或1
		:return:client
		"""
		client = snap7.client.Client()
		client.set_connection_type(type)
		client.connect(ip, rack, slot)
		return client

	def plc_con_close(self,client):
		"""
		连接关闭
		:param client:
		:return:
		"""
		client.disconnect()


	def read_VB(self,client, offset):
		""" :param client: client
			:param offset: int 
			:returns: str.
		"""
		vb_data = client.db_read(1, offset, 1)
		return vb_data[0]

	def write_VB(self,client, offset, data):
		""" :param client: client
			:param offset: int 
			:param data: str
		"""
		data = int(data)
		temp = hex(int(data))[2:]
		if data < 0 or data > 255:
			print("请输入0-255之间的数")
		else:
			if data < 16:
				temp = "0"+ temp
			client.db_write(1, offset, bytes.fromhex(temp))
			print("向寄存器VB"+str(offset)+"写入"+str(data)+"成功")
			
	def write_VD(self,client, offset, data):

		temp = hex(int(data))
		temp = temp[2:].zfill(8)
		# print(type(temp))
		try:
			client.write_area(snap7.client.Areas.DB, 1, offset, bytes.fromhex(temp))
			print("向寄存器VD"+str(offset)+"写入"+str(data)+"成功")
		except Exception as e:
			time.sleep(0.003)
			self.write_VD(client, offset, data)

	def read_VD(self,client, offset):
		"""This is a lean function of Cli_ReadArea() to read PLC DB.
			:param client: client
			:param offset
			:returns: data int.
		"""
		try:
			v_data = client.read_area(snap7.client.Areas.DB, 1, offset, 4)
			data = int.from_bytes(v_data, byteorder='big', signed=False)
		except Exception as e:
			time.sleep(0.003)
			data = self.read_VD(client, offset)
		return data
	def write_VW(self,client, offset, data):

		temp = hex(int(data))
		temp = temp[2:].zfill(4)
		# print(type(temp))
		try:
			client.write_area(snap7.client.Areas.DB, 1, offset, bytes.fromhex(temp))
			print("向寄存器VW"+str(offset)+"写入"+str(data)+"成功")
		except Exception as e:
			time.sleep(0.003)
			self.write_VW(client, offset, data)

	def read_VW(self,client, offset):
		"""This is a lean function of Cli_ReadArea() to read PLC DB.
			:param client: client
			:param offset
			:returns: data int.
		"""
		try:
			v_data = client.read_area(snap7.client.Areas.DB, 1, offset, 2)
			data = int.from_bytes(v_data, byteorder='big', signed=False)
		except Exception as e:
			time.sleep(0.003)
			data = self.read_VW(client, offset)
		return data

	def check_key(self):
		if keyboard.is_pressed('esc'):
			return True
		else:
			return False
		

	def send_data(self,num):
		self.write_VW(self.client_fd, 500, str(num))

	def receive_data(self,q_in):
		
		init_time = time.time()
		print("Enter data received process---")
		data = []
		data_output_list = []
		output_time = 0
		while(True):
			if self.check_key():
				break
			
			# data_get = q_in.get()
			# if data_get is _sentinel:
			# 	break


			cur_time = time.time()-init_time
			vacuum = self.read_VW(self.client_fd, 1000)
			vacuum = round((-0.018*(vacuum-3920)+79.3),2)
			# print(vacuum)
			current = self.read_VW(self.client_fd, 2000)
			voltage = self.read_VD(self.client_fd, 2002)
			power = self.read_VW(self.client_fd, 2006)

			if len(data_output_list)<5:
				data_output_list.append([vacuum,power])
			else: 
				vacuum_output = np.mean(data_output_list,axis=0)[0]
				power_output  = np.mean(data_output_list,axis=0)[1]
				vacuum_rate_output = (data_output_list[-1][0]-data_output_list[0][0])/(cur_time-output_time)
				data_output_list = []
				output_time = cur_time
				q_in.put([output_time,vacuum_output,vacuum_rate_output,power_output/1000])

			# print(data)
			data.append([cur_time,vacuum,current/1000,voltage/1000,power/1000])


			time.sleep(0.01)

		q_in.put(_sentinel)
		# save org data
		# data_xlsx = pd.DataFrame(data)
		# writer = pd.ExcelWriter('./data.xlsx')
		# data_xlsx.to_excel(writer,sheet_name='page_1')
		# writer.close()
		
	def close(self):
		self.plc_con_close(self.client_fd)

if __name__ == "__main__":
	plc_test = PC_PLC('192.168.58.20')
	plc_test.receive_data()
	plc_test.send_data(1)
	plc_test.close()
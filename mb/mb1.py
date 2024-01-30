#from modbus.client import *
#from pymodbus.client import ModbusTcpClient
import time
import easymodbus.modbusClient
modbus_client = easymodbus.modbusClient.ModbusClient('192.168.123.100')
modbus_client.connect()
for i in range(5):
	print(modbus_client.read_holdingregisters(0, 5))
	time.sleep(1)
modbus_client.close()
#c = ModbusTcpClient('192.168.123.100')
#c.connect()
#print(c.read_holding_registers(40001, 6, slave=1))
#read([400001,400002,400003,400004]))
#c.close()
import time
from pymodbus.client import ModbusTcpClient
c = ModbusTcpClient('192.168.123.100')
x = ()
while not x:
    print('.')
    time.sleep(1)
    x = c.read_holding_registers(40001, 6,255)
print(x)
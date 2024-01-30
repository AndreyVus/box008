import time
from pyModbusTCP.client import ModbusClient
c = ModbusClient(host='192.168.123.100', port=502, debug=True, timeout=5, auto_open=True, auto_close=True)
x = ()
while not x:
    print('.')
    time.sleep(1)
    x = c.read_holding_registers(40001, 6)
print(x)
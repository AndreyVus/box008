from pymodbus3.client.sync import ModbusTcpClient

client = ModbusTcpClient('192.168.123.100')
result = client.read_holding_registers(1,1)
print(result)
client.close()

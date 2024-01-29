node = {
	'Tanktemp'    : 2,
	'Tankniveau'  : 3,
	'Volumenstrom': 4,
}
opc = 'opc.tcp://192.168.123.100:4840'
db_name = 'telemetry'
measurement = 'opc'


while True:
	try:
		import re           # 1
		import syslog       # 2
		import subprocess   # 3
		from influxdb import InfluxDBClient
		from opcua import Client
		break
	except Exception as err:
		e2 = re.findall("'(.+)'", str(err))[0]
		syslog.syslog(syslog.LOG_WARNING, f'{err}. Install {e2}')
		subprocess.run(['pip', 'install', e2])
# connect influx
InfluxClient = InfluxDBClient()
# use telemetry
InfluxClient.switch_database(db_name)
# connect opc
OpcClient = Client(opc)
OpcClient.session_timeout = 1000
OpcClient.connect()
InfluxClient.write_points([{
	'measurement': measurement,
	'fields'     : {k: OpcClient.get_node(f'ns=4;i={v}').get_value() for k, v in node.items()}
}])
OpcClient.disconnect()
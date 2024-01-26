node = {
	'Tanktemp'    : 2,
	'Tankniveau'  : 3,
	'Volumenstrom': 4,
}
opc = 'opc.tcp://192.168.123.100:4840'
db_name = 'telemetry'
measurement = 'opc'
from influxdb import InfluxDBClient
from opcua import Client
from time import sleep
import sys
try:
	Periode = int(sys.argv[1])
	# connect influx
	InfluxClient = InfluxDBClient()
	# use telemetry
	InfluxClient.switch_database(db_name)
	# connect opc
	OpcClient = Client(opc)
	OpcClient.session_timeout = 1000
	OpcClient.connect()
	while True:
		InfluxClient.write_points([{
			'measurement': measurement,
			'fields'     : {k: OpcClient.get_node(f'ns=4;i={v}').get_value() for k, v in node.items()}
		}])
		sleep(Periode)
except:
	exit(1)
from datetime import datetime
from influxdb import InfluxDBClient
from time import sleep
import requests
import sys
import syslog


Periode = int(sys.argv[1])
settings = {
	'ThingsBoardToken': 'http://thingsboard.kbw-cloud.de/api/v1/box008/telemetry',
	'db_name': 'telemetry',
	'measurement': {
		'opc': {# holen die letzte Stunde Mittelwerte
			'Query': f'SELECT MEAN(Tanktemp) AS Tanktemp, MEAN(Tankniveau) AS Tankniveau, MEAN(Volumenstrom) AS Volumenstrom FROM opc GROUP BY time({Periode}s) fill(none) ORDER BY time DESC LIMIT {int(3600/Periode)}'
		},
		'host': {
			'Query': 'select * from host order by time desc limit 1',
		}
	}
}


def DataTS(Query):
	return [{'ts': values.pop('time'), 'values': values} for values in InfluxClient.query(Query, params={'epoch': 'ms'}).get_points()]


try:
	# connect influx
	InfluxClient = InfluxDBClient()
	# use telemetry
	InfluxClient.switch_database(settings['db_name'])
	while True:
		data = DataTS(settings['measurement']['opc']['Query']) + DataTS(settings['measurement']['host']['Query'])
		# nach ThingsBoard senden
		response = requests.post(settings['ThingsBoardToken'], data=str(data).encode('utf-8'),
			timeout=5, headers={'Content-Type': 'application/json; charset=UTF-8'})
		if 200 != response.status_code:
			syslog.syslog(syslog.LOG_WARNING, f'Error sending nach TB {response.status_code}')
		sleep(Periode)
except:
	exit(1)
ThingsBoardToken = 'http://thingsboard.kbw-cloud.de/api/v1/box008/telemetry'
db_name = 'telemetry'
# 120s und 3600/120
opc_Query = 'SELECT MEAN(Tanktemp) AS Tanktemp, MEAN(Tankniveau) AS Tankniveau, MEAN(Volumenstrom) AS Volumenstrom FROM opc GROUP BY time(120s) fill(none) ORDER BY time DESC LIMIT 30'
host_Query = 'SELECT * FROM host ORDER BY time DESC LIMIT 1'


while True:
	try:
		import re           # 1
		import syslog       # 2
		import subprocess   # 3
		from influxdb import InfluxDBClient
		import requests
		break
	except Exception as err:
		e2 = re.findall("'(.+)'", str(err))[0]
		syslog.syslog(syslog.LOG_WARNING, f'{err}. Install {e2}')
		subprocess.run(['pip', 'install', e2])
def DataTS(Query):
	return [{'ts': values.pop('time'), 'values': values} for values in InfluxClient.query(Query, params={'epoch': 'ms'}).get_points()]
# connect influx
InfluxClient = InfluxDBClient()
# use telemetry
InfluxClient.switch_database(db_name)
data = DataTS(opc_Query) + DataTS(host_Query)
# nach ThingsBoard senden
response = requests.post(ThingsBoardToken, data=str(data).encode('utf-8'),
	timeout=5, headers={'Content-Type': 'application/json; charset=UTF-8'})
if 200 != response.status_code:
	syslog.syslog(syslog.LOG_WARNING, f'Error sending nach TB {response.status_code}')
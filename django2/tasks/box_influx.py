db_name = 'telemetry'
measurement = 'host'


while True:
	try:
		import re           # 1
		import syslog       # 2
		import subprocess   # 3
		from influxdb import InfluxDBClient
		from math import log10
		import psutil
		break
	except Exception as err:
		e2 = re.findall("'(.+)'", str(err))[0]
		syslog.syslog(syslog.LOG_WARNING, f'{err}. Install {e2}')
		subprocess.run(['pip', 'install', e2])


def kiloMegaGiga(x):
	f = [[1, ''], [1e3, 'k'], [1e6, 'M'], [1e9, 'G']]
	i = max(0, min(3, int(log10(x) // 3)))
	return f'{x / f[i][0]:.1f} {f[i][1]}'


# connect influx
InfluxClient = InfluxDBClient()
# use telemetry
InfluxClient.switch_database(db_name)


# nach influx
InfluxClient.write_points([{
	'measurement': measurement,
	'fields'     : {
		'IP VPN'            : psutil.net_if_addrs().get('tun0', [''])[0].address,
		'WLAN LTE Status'   : subprocess.check_output("ssid=$(iwgetid -r)||ssid='no';echo $ssid",shell=True).decode().strip(),
		'CPU Temperatur, °C': subprocess.check_output(['vcgencmd', 'measure_temp']).decode()[5:-3],
		'CPU Usage, %'      : psutil.cpu_percent(interval=1),
		'Free RAM'          : kiloMegaGiga(psutil.virtual_memory().free) + 'b',
		'Free Disk'         : kiloMegaGiga(psutil.disk_usage('.').free) + 'b'
	}
}])
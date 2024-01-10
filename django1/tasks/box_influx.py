db_name = 'telemetry'
measurement = 'host'


from influxdb import InfluxDBClient
from math import log10
from time import sleep
import psutil
import subprocess
import sys


def kiloMegaGiga(x):
	f = [[1, ''], [1e3, 'k'], [1e6, 'M'], [1e9, 'G']]
	i = max(0, min(3, int(log10(x) // 3)))
	return f'{x / f[i][0]:.1f} {f[i][1]}'

try:
	Periode = int(sys.argv[1])
	# connect influx
	InfluxClient = InfluxDBClient()
	# use telemetry
	InfluxClient.switch_database(db_name)
	while True:
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
		sleep(Periode)
except:
	exit(1)
import math
import paho.mqtt.publish as publish
import psutil
import requests
import subprocess


if 200 == requests.get('http://10.8.0.1:8055', timeout=5).status_code:
	publish.single('LED_VPN', 1)


	def kiloMegaGiga(x):
		f = [[1, ''], [1e3, 'k'], [1e6, 'M'], [1e9, 'G']]
		i = max(0, min(3, int(math.log10(x) // 3)))
		return f'{x / f[i][0]:.1f} {f[i][1]}'


	print({
		'IP VPN'            : psutil.net_if_addrs().get('tun0', [''])[0].address,
		'WLAN LTE Status'   : subprocess.check_output("ssid=$(iwgetid -r)||ssid='no';echo $ssid", shell=True).decode().strip(),
		'CPU Temperatur, °C': subprocess.check_output(['vcgencmd', 'measure_temp']).decode()[5:-3],
		'CPU Usage, %'      : psutil.cpu_percent(interval=1),
		'Free RAM'          : kiloMegaGiga(psutil.virtual_memory().free) + 'b',
		'Free Disk'         : kiloMegaGiga(psutil.disk_usage('.').free) + 'b'
	})
else:
	publish.single('LED_VPN', 0)
#!/usr/bin/python
FILE = '/etc/systemd/system/kbwio.service'
tasks_db = '/home/kbwiot/tasks_db.sqlite3'


while True:
	try:
		import re           # 1
		import syslog       # 2
		import subprocess   # 3
		import os
		import requests
		import sqlite3
		import sys
		import threading#
		import time
		break
	except Exception as err:
		e2 = re.findall("'(.+)'", str(err))[0]
		syslog.syslog(syslog.LOG_WARNING, f'{err}. Install {e2}')
		subprocess.run(['pip', 'install', e2])


def DI(x):
	with open(f'/sys/class/gpio/gpio{18 + x}/value') as f:
		ans = f.read(1) == '0'
	return ans


def DO(x, value):
	with open(f'/sys/class/gpio/gpio{22 + x}/value', 'w') as f:
		f.write(value)


def DIO(x, value):
	with open(f'/sys/class/gpio/gpio{496 + x}/value', 'w') as f:
		f.write(value)
	with open(f'/sys/class/gpio/gpio{500 + x}/value') as f:
		ans = f.read(1) == '0'
	return ans


def LED_RED(value):
	with open('/sys/devices/platform/leds/leds/LED1/brightness', 'w') as f:
		f.write(value)
	#with open('/sys/class/leds/LED1/brightness') as f:
	#	ans = f.read(1) != '0'
	#return ans


def LED_GREEN(value):
	with open('/sys/devices/platform/leds/leds/LED2/brightness', 'w') as f:
		f.write(value)
	#with open('/sys/class/leds/LED2/brightness') as f:
	#	ans = f.read(1) != '0'
	#return ans


def BEEP(value):
	with open('/sys/devices/platform/leds/leds/BUZZER/brightness', 'w') as f:
		f.write(value)
	#with open('/sys/class/leds/BUZZER/brightness') as f:
	#	ans = f.read(1) != '0'
	#return ans


def AI(x):
	with open(f'/sys/bus/iio/devices/iio:device0/in_voltage{x}_raw') as f:
		ans = f.readline()
	return float(ans) / 2816


def start():
	if not os.path.isfile(FILE):
		with open(FILE, 'w') as f:
			f.write('''[Unit]
Description=kbwio
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/kbwiot
ExecStart=/home/kbwiot/KbwIO.py
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
''')
	subprocess.run(['systemctl', 'enable', 'kbwio.service'])
	subprocess.run(['systemctl', 'start', 'kbwio.service'])
	subprocess.run(['systemctl', 'status', 'kbwio.service'])


def stop():
	subprocess.run(['systemctl', 'stop', 'kbwio.service'])  # Stoppen Sie den Dienst
	subprocess.run(['systemctl', 'disable', 'kbwio.service'])  # Deaktivieren Sie den Dienst
	subprocess.run(['rm', FILE])  # Löschen Sie die Dienstdatei
	subprocess.run(['systemctl', 'daemon-reload'])  # Neuladen der systemd-Konfiguration, um die Änderungen zu übernehmen


def puls_blinker():
	while True:
		LED_RED('1')
		time.sleep(0.2)
		LED_RED('0')
		time.sleep(1.8)


def tasks():
	while True:
		# get joblist from db
		with sqlite3.connect(tasks_db) as conn:
			c = conn.cursor()
			c.execute('SELECT id, Name, Periode, Start, skript FROM home_db1 WHERE Berechtigen = 1;')
			joblist = {
				Nr: {'Name': Name, 'Periode': Periode, 'Start': Start, 'skript': skript}
				for (Nr, Name, Periode, Start, skript) in c.fetchall()
			}
		if joblist:
			#syslog.syslog(syslog.LOG_INFO, f"joblist {joblist}")
			# Zyklus 1 Minute
			endTime = time.time() + 60
			while time.time() < endTime:
				for job in joblist.values():
					if job['Start'] <= time.time():
						#syslog.syslog(syslog.LOG_INFO, f"{job['Name']} 1")
						# nächste Startzeit, s
						job['Start'] = time.time() + job['Periode']
						if 0 != subprocess.run(['python', '-c', job['skript']]).returncode:
							syslog.syslog(syslog.LOG_WARNING, f"tasks.py: Error {job['Name']}")
						#syslog.syslog(syslog.LOG_INFO, f"{job['Name']} 0")
				# positive pause bis nächstes job
				time.sleep(max(0, min([job['Start'] for job in joblist.values()]) - time.time()))
			# save start Werte
			with sqlite3.connect(tasks_db) as conn:
				c = conn.cursor()
				for Nr, values in joblist.items():
					c.execute(
						'UPDATE home_db1 SET start=? WHERE id=?;', (values['Start'], Nr)
					)
		else:
			#syslog.syslog(syslog.LOG_INFO, 'sleep 60')
			time.sleep(60)


if __name__ == '__main__':
	wv = os.path.isfile('/etc/systemd/system/wvdial.service')
	args = sys.argv[1:]
	if 'start' in args:
		start()
	elif 'stop' in args:
		stop()
	else:
		#init()
		for x in [18, 19, 20, 21, 500, 501, 502, 503]:  # DI
			if not os.path.exists(f'/sys/class/gpio/gpio{x}/value'):
				with open('/sys/class/gpio/export', 'w') as f:
					f.write(str(x))
			with open(f'/sys/class/gpio/gpio{x}/direction', 'w') as f:
				f.write('in')
		for x in [22, 23, 24, 25, 496, 497, 498, 499]:  # DO
			if not os.path.exists(f'/sys/class/gpio/gpio{x}/value'):
				with open('/sys/class/gpio/export', 'w') as f:
					f.write(str(x))
			with open(f'/sys/class/gpio/gpio{x}/direction', 'w') as f:
				f.write('out')
		# Skalierung #####################################
		# 28160 raw = 10V --> faktor = 1/2816
		with open('/sys/bus/iio/devices/iio:device0/in_voltage_sampling_frequency', 'w') as f:
			f.write('15')
		#
		#run()
		# blinker
		threading.Thread(target=puls_blinker).start()
		# tasks_db.sqlite3
		threading.Thread(target=tasks).start()
		# vpn-check
		while True:
			time.sleep(60)
			if 200 == requests.get('http://10.8.0.1:8055', timeout=5).status_code:
				LED_GREEN('1')
				if wv:
					subprocess.run(
						'if ping 1.1.1.1 -c 1 -W 5 -I wlan0 || ping 1.1.1.1 -c 1 -W 5 -I eth0; then systemctl stop wvdial; fi',
						shell=True, stdout=subprocess.DEVNULL
					)
			else:
				LED_GREEN('0')
				if wv:
					subprocess.run('systemctl restart wvdial', shell=True, stdout=subprocess.DEVNULL)
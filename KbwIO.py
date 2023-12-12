#!/usr/bin/python
from time import sleep
import os
import requests
import subprocess
import sys
import threading


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


FILE = '/etc/systemd/system/kbwio.service'
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
		sleep(0.2)
		LED_RED('0')
		sleep(1.8)


def init():
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


def run():
	# blinker und vpn-check
	threading.Thread(target=puls_blinker).start()
	while True:
		sleep(60)
		if 200 == requests.get('http://10.8.0.1:8055', timeout=5).status_code:
			LED_GREEN(1)
			if wv:
				subprocess.run(
					'if ping 1.1.1.1 -c 1 -W 5 -I wlan0 || ping 1.1.1.1 -c 1 -W 5 -I eth0; then systemctl stop wvdial; fi',
					shell=True, stdout=subprocess.DEVNULL
				)
		else:
			LED_GREEN(0)
			if wv:
				subprocess.run('systemctl restart wvdial', shell=True, stdout=subprocess.DEVNULL)


if __name__ == '__main__':
	wv = os.path.isfile('/etc/wvdial.conf')
	args = sys.argv[1:]
	if 'start' in args:
		start()
	elif 'stop' in args:
		stop()
	else:
		init()
		run()
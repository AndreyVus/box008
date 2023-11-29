#!/bin/python
import cryptocode
import os
import re
import subprocess
import sys
import syslog
import sqlite3
import yaml


def decode(passw):
	if len(passw) > 20:
		passw = cryptocode.decrypt(passw, 'Kbwiot2022!')
	return passw


def nmcli_c():
	return subprocess.check_output("nmcli c | awk '/wifi/ {print $1}'", shell=True).decode().split()


def nmcli_add(ssid, passw):
	subprocess.run(['nmcli', 'con', 'add', 'ifname', 'wlan0', 'con-name', f'{ssid}', 'type', 'wifi',
					'ssid', f'{ssid}', 'ipv4.route-metric', '150', 'wifi-sec.key-mgmt', 'wpa-psk',
					'wifi-sec.psk', f'{passw}'])


def nmcli_del(datei):
	subprocess.run(['nmcli', 'connection', 'delete', datei])


def hat(datei, ssid, passw):
	pat = re.compile(f'(ssid={ssid}$).+(psk={passw}$)', re.M+re.S)
	try:
		with open(f'/etc/NetworkManager/system-connections/{datei}.nmconnection') as file:
			return pat.findall(file.read())
	except:
		return []


def start():
	if not os.path.exists(link):
		subprocess.run(["ln", "-s", os.path.realpath(__file__), link])


def stop():
	if os.path.exists(link):
		subprocess.run(["rm", link])


def run():
	try:
		with sqlite3.connect('/home/kbwiot/django1/db.sqlite3') as conn:
			c=conn.cursor()
			c.execute('SELECT Einstellungen FROM home_db2 WHERE id=1;')
			wifi = yaml.safe_load(c.fetchone()[0])['wifi']
		for datei in set(nmcli_c()).difference(set(wifi.keys())):
			nmcli_del(datei)
		for datei in nmcli_c():
			flag = True
			for ssid, passw in wifi.items():
				if hat(datei, ssid, decode(passw)):
					flag = False
					break
			if flag:
				nmcli_del(datei)
		for ssid in set(wifi.keys()).difference(set(nmcli_c())):
			nmcli_add(ssid, decode(wifi[ssid]))
	except Exception as e:
		syslog.syslog(syslog.LOG_WARNING, f'KbwWlan.py: {e}')


if __name__ == '__main__':
	link = '/etc/cron.daily/kbwwlan.py'
	args = sys.argv[1:]
	if 'start' in args:
		start()
	elif 'stop' in args:
		stop()
	else:
		run()
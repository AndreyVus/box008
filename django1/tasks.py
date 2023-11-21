#!/usr/bin/python
import requests
import subprocess
import syslog
import sqlite3
import time
import yaml


with sqlite3.connect('db.sqlite3') as conn:
	c=conn.cursor()
	c.execute('SELECT Einstellungen FROM home_db2 WHERE id=1;')
	ThingsBoardToken = yaml.safe_load(c.fetchone()[0])['ThingsBoardToken']
while True:
	# get joblist from db
	with sqlite3.connect('db.sqlite3') as conn:
		c = conn.cursor()
		c.execute('SELECT id, Name, Periode, start, skript FROM home_db1 WHERE Berechtigen = 1;')
		joblist = {
			Nr: {'Name': Name, 'Periode': Periode, 'start': start, 'skript': skript}
			for (Nr, Name, Periode, start, skript) in c.fetchall()
		}
	# print(joblist)
	if joblist:
		# Zyklus 1 Minute
		endTime = time.time() + 60
		while time.time() < endTime:
			for job in joblist.values():
				if job['start'] <= time.time():
					# nächste Startzeit
					job['start'] = time.time() + job['Periode']
					try:
						data = subprocess.check_output(['python', '-c', job['skript']]).decode().strip()
					except Exception as e:
						syslog.syslog(syslog.LOG_WARNING, f"tasks.py: {job['Name']}, {e}")
						data = {job['Name']: 'error'}
					# send json to ThingsBoard
					response = requests.post(ThingsBoardToken, data=data, timeout=5)
					if response.status_code != 200:
						syslog.syslog(syslog.LOG_WARNING, f'tasks.py: Error sending telemetry {response.status_code}')
			# positive pause bis nächstes job
			time.sleep(max(0, min([job['start'] for job in joblist.values()]) - time.time()))
		# save start Werte
		with sqlite3.connect('db.sqlite3') as conn:
			c = conn.cursor()
			for Nr, values in joblist.items():
				c.execute(
					'UPDATE db1 SET start=? WHERE id=?;', (values['start'], Nr)
				)
	else:
		time.sleep(60)
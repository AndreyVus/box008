#!/usr/bin/python
db = '/home/kbwiot/django1/db.sqlite3'
import sqlite3
import subprocess
import syslog
import time


# # connect
# InfluxClient = InfluxDBClient()
# db_name = 'telemetry'
# # create, wenn db fehlt
# if not any(d['name'] == db_name for d in InfluxClient.get_list_database()):
#	 InfluxClient.create_database(db_name)
#	 InfluxClient.create_retention_policy('one_hour_policy', '1h', 1, db_name, default=True)
# # use telemetry
# InfluxClient.switch_database(db_name)

while True:
	# get joblist from db
	with sqlite3.connect(db) as conn:
		c = conn.cursor()
		c.execute('SELECT id, Name, Periode, start, skript FROM home_db1 WHERE Berechtigen = 1;')
		joblist = {
			Nr: {'Name': Name, 'Periode': Periode, 'start': start, 'skript': skript}
			for (Nr, Name, Periode, start, skript) in c.fetchall()
		}
	if joblist:
		#print(joblist)
		# Zyklus 1 Minute
		endTime = time.time() + 60
		while time.time() < endTime:
			for job in joblist.values():
				if job['start'] <= time.time():
					# nächste Startzeit #, ms --> s
					job['start'] = time.time() + job['Periode']#/1000
					print(job['Name'])
					if 0!=subprocess.run(['python', '-c', job['skript']]).returncode:
						syslog.syslog(syslog.LOG_WARNING, f"tasks.py: Error {job['Name']}")#, {e}")
			break
			# positive pause bis nächstes job
			time.sleep(max(0, min([job['start'] for job in joblist.values()]) - time.time()))
		# save start Werte
		with sqlite3.connect(db) as conn:
			c = conn.cursor()
			for Nr, values in joblist.items():
				c.execute(
					'UPDATE home_db1 SET start=? WHERE id=?;', (values['start'], Nr)
				)
	else:
		break
		time.sleep(60)
	break
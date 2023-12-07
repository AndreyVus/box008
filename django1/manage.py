#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
from time import sleep
import multiprocessing
import os
import psutil
import sqlite3
import subprocess
import sys
import syslog


db = '/home/kbwiot/django1/db.sqlite3'
# # connect
# InfluxClient = InfluxDBClient()
# db_name = 'telemetry'
# # create, wenn db fehlt
# if not any(d['name'] == db_name for d in InfluxClient.get_list_database()):
#	 InfluxClient.create_database(db_name)
#	 InfluxClient.create_retention_policy('one_hour_policy', '1h', 1, db_name, default=True)
def wachter():
	while True:
		# get joblist from db
		with sqlite3.connect(db) as conn:
			c = conn.cursor()
			c.execute('SELECT id, Berechtigen, Name, Periode, skript FROM home_db1;')
			joblist = {
				Nr: {'Berechtigen': Berechtigen, 'Name': Name, 'Periode': Periode, 'skript': skript}
				for (Nr, Berechtigen, Name, Periode, skript) in c.fetchall()
			}
		for job in joblist.values():
			# create Name.py
			tasks_py = '/tmp/'+job['Name']
			if job['Berechtigen']:
				with open(tasks_py, 'w', encoding='utf-8') as f:
					f.write(job['skript'].replace('Periode', str(joblist['Periode'])))
				#if not runned(Name):
					#start(Name, Periode, skript)
				f = True
				for p in psutil.process_iter(['pid', 'cmdline']):
					if tasks_py == p.info['cmdline']:
						f = False
						break
				if f:
					subprocess.Popen(['/bin/python', '-c', tasks_py])
					syslog.syslog(syslog.LOG_INFO, f'python {tasks_py} startet')
			else:
				#if runned(Name):
					#stop(Name)
				for p in psutil.process_iter(['pid', 'cmdline']):
					if tasks_py == p.info['cmdline']:
						p.kill()
						syslog.syslog(syslog.LOG_INFO, f'python {tasks_py} stopped')
						break
		sleep(60)


def main():
	"""Run administrative tasks."""
	os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
	try:
		from django.core.management import execute_from_command_line
	except ImportError as exc:
		raise ImportError(
			"Couldn't import Django. Are you sure it's installed and "
			"available on your PYTHONPATH environment variable? Did you "
			"forget to activate a virtual environment?"
		) from exc
	execute_from_command_line(sys.argv)


if __name__ == '__main__':
	syslog.syslog(syslog.LOG_INFO, 'django start')
	multiprocessing.Process(target=wachter).start()
	main()
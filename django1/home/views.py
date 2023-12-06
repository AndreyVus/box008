from .models import db1, db2
from django.shortcuts import render, redirect
import subprocess
import syslog
import yaml
p = None

def einstellungen(request):
	try:
		item = db2.objects.get(id=1)
	except:
		db2.objects.create(id=1)
		item = db2.objects.get(id=1)
	if request.method == 'POST':
		try:
			d1 = yaml.safe_load(request.POST['Einstellungen'])
			item.Einstellungen = yaml.dump(d1, default_flow_style=False, allow_unicode=True)
		except Exception as e:
			item.Einstellungen = e
		item.save()
	return render(request, 'settings.html', {"Einstellungen": item.Einstellungen})


def home(request):
	if request.method == 'POST':
		item = db1.objects.get(id=request.POST['Nr'])
		Tat = request.POST['Tat']
		if Tat == 'Berechtigen':
			item.Berechtigen = request.POST['Wert'] == 'true'
		elif Tat == 'Name':
			item.Name = request.POST['Wert']
		elif Tat == 'Periode':
			item.Periode = request.POST['Wert']
		elif Tat == 'skript':
			item.skript = request.POST['Wert']
		item.save()
	return render(request, 'tasks.html', {
		'all_items': db1.objects.all(),
	})


def addItem(request):
	db1.objects.create(Name='new job')
	return redirect('/')


def delItem(request):
	item = db1.objects.get(id=request.GET['Nr'])
	item.delete()
	return redirect('/')


def editItem(request):
	if request.method == 'GET':
		Nr = request.GET['Nr']
		item = db1.objects.get(id=Nr)
		return render(request, 'editjob.html', {'Nr': Nr, 'Name': item.Name, 'skript': item.skript})
	#return redirect('/')


def start(request):
	global p
	tasks_py = '/home/kbwiot/django1/tasks.py'
	ans = db1.objects.filter(Berechtigen=True).values('Name', 'Periode', 'skript')
	with open(tasks_py, 'w', encoding='utf-8') as f:
		f.write('#!/usr/bin/python\rfrom time import sleep\rimport syslog, threading\rlock = threading.Lock()\r')
		for a in ans:
			f.write(f"\rdef task_{a['Name'].replace(' ', '_')}(Periode):\r\t")
			f.write(a['skript'].replace('\r\n', '\r\t').replace('\t\r', ''))
		f.write('\r# Threads für jede Aufgabe\rpool = [\r')
		for a in ans:
			f.write(f"\tthreading.Thread(target=task_{a['Name'].replace(' ', '_')}, args=({a['Periode']},)),\r")
		f.write(']\r[t.start() for t in pool]\rwhile all([t.is_alive() for t in pool]):\r\tsleep(60)\r')
		f.write("syslog.syslog(syslog.LOG_WARNING, 'Einige Threads wurden in tasks.py gestoppt.')")
	p = subprocess.Popen(['/bin/python', tasks_py])
	syslog.syslog(syslog.LOG_INFO, 'python tasks_py startet')
	return redirect('/')


def stop(request):
	global p
	if p:
		p.kill()
		p.wait()
		p = None
		syslog.syslog(syslog.LOG_INFO, 'python tasks_py stopped')
	return redirect('/')
from .models import db1, db2
from django.shortcuts import render, redirect
import os
import subprocess
import yaml
skript_path = '/home/kbwiot/django1/tasks/'


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
	return render(request, 'settings.html', {
		'Einstellungen': item.Einstellungen,
	})


def start_skript(item):
	skript_py = f'{skript_path}{item.Name}.py'
	SERVICE = f'/etc/systemd/system/{item.Name}.service'
	#write unit
	#start unit
	with open(skript_py, 'w') as f:
		f.write(item.skript)
	with open(SERVICE, 'w') as f:
		f.write(f'''[Unit]
Description={item.Name}.service
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/kbwiot/django1
ExecStart=/bin/python {skript_py} {item.Periode}
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
''')
	subprocess.run(['systemctl', 'enable', f'{item.Name}.service'])
	subprocess.run(['systemctl', 'start', f'{item.Name}.service'])
	#subprocess.run(['systemctl', 'status', f'{item.Name}'.service])


def stop_skript(item):
	skript_py = f'{skript_path}{item.Name}.py'
	SERVICE = f'/etc/systemd/system/{item.Name}.service'
	#stop unit
	#del unit
	if os.path.isfile(SERVICE):
		subprocess.run(['systemctl', 'stop', f'{item.Name}.service'])  # Stoppen Sie den Dienst
		os.remove(SERVICE)  # Löschen Sie die Dienstdatei
		os.remove(skript_py)
		subprocess.run(['systemctl', 'daemon-reload'])  # Neuladen der systemd-Konfiguration, um die Änderungen zu übernehmen


def home(request):
	if request.method == 'POST':
		item = db1.objects.get(id=request.POST['Nr'])
		Tat = request.POST['Tat']
		if Tat == 'Berechtigen':
			item.Berechtigen = request.POST['Wert'] == 'true'
			if item.Berechtigen:
				start_skript(item)
			else:
				stop_skript(item)
		elif Tat == 'Name':
			item.Name = request.POST['Wert'].replace(' ', '_')
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
	stop_skript(item)
	item.delete()
	return redirect('/')


def editItem(request):
	if request.method == 'GET':
		Nr = request.GET['Nr']
		item = db1.objects.get(id=Nr)
		item.Berechtigen = False
		item.save()
		stop_skript(item)
		return render(request, 'editjob.html', {
			'Nr': Nr,
			'Name': item.Name,
			'skript': item.skript,
		})
	#return redirect('/')
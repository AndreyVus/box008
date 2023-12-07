from .models import db1, db2
from django.shortcuts import render, redirect
import yaml


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


def home(request):
	if request.method == 'POST':
		item = db1.objects.get(id=request.POST['Nr'])
		Tat = request.POST['Tat']
		if Tat == 'Berechtigen':
			item.Berechtigen = request.POST['Wert'] == 'true'
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
	item.delete()
	return redirect('/')


def editItem(request):
	if request.method == 'GET':
		Nr = request.GET['Nr']
		item = db1.objects.get(id=Nr)
		return render(request, 'editjob.html', {
			'Nr': Nr,
			'Name': item.Name,
			'skript': item.skript,
		})
	#return redirect('/')
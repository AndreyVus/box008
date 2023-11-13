from django.shortcuts import render, redirect
from .models import db1, db2


def einstellungen(request):
    item = db2.objects.get(id=1)
    if request.method == 'POST':
        item.Einstellungen = request.POST['Einstellungen'].encode('utf-8')
        item.save()
    return render(request, 'template1.html', {"Einstellungen": item.Einstellungen})


def home(request):
    if request.method == 'POST':
        item = db1.objects.get(id=request.POST['Nr'])
        Tat = request.POST['Tat']
        if Tat == 'Berechtigen':
            item.Berechtigen = request.POST['Wert'] == 'true'
            item.start = 1
        elif Tat == 'Name':
            item.Name = request.POST['Wert']
        elif Tat == 'Periode':
            item.Periode = request.POST['Wert']
            item.start = 1
        elif Tat == 'skript':
            item.skript = request.POST['Wert'].encode('utf-8')
        item.save()
    return render(request, 'template2.html', {
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
        return render(request, 'template3.html', {'Nr': Nr, 'Name': item.Name, 'skript': item.skript.decode()})
    #return redirect('/')
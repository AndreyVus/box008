from django.shortcuts import render, redirect
from .models import home1Item


def einstellungen(request):
    item = home2Item.objects.get(id=1)
    if request.method == 'POST':
        item.Einstellungen = request.POST['Einstellungen'].encode('utf-8')
        item.save()
    return render(request, 'template1.html', {"Einstellungen": item})


def home(request):
    if request.method == 'POST':
        item = home1Item.objects.get(id=request.POST['Nr'])
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
        'all_items': home1Item.objects.all(),
    })


def addItem(request):
    home1Item.objects.create(Name='new job')
    return redirect('/')


def delItem(request):
    item = home1Item.objects.get(id=request.GET['Nr'])
    item.delete()
    return redirect('/')


def editItem(request):
    if request.method == 'GET':
        Nr = request.GET['Nr']
        item = home1Item.objects.get(id=Nr)
        return render(request, 'template3.html', {'Nr': Nr, 'Name': item.Name, 'skript': item.skript.decode()})
    #return redirect('/')
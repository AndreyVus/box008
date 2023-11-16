from django.urls import path
from home import views

urlpatterns = [
	path('settings/', views.einstellungen),
	path('add/', views.addItem),
	path('del/', views.delItem),
	path('edit/', views.editItem),
	path('', views.home),
]
from django.db import models

# Create your models here.
class db1(models.Model):
	Berechtigen = models.BooleanField(default=False)
	Name = models.CharField(max_length=50)
	Periode = models.PositiveIntegerField(default=1)
	start = models.PositiveIntegerField(default=1)
	skript = models.TextField(max_length=65000)


class db2(models.Model):
	Einstellungen = models.TextField(max_length=65000)
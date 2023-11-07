from django.db import models

# Create your models here.
class home1Item(models.Model):
	Berechtigen = models.BooleanField(default=False)
	Name = models.CharField(max_length=50)
	Periode = models.PositiveIntegerField(default=1)
	start = models.PositiveIntegerField(default=1)
	skript = models.BinaryField(max_length=65000)


class home2Item(models.Model):
	Einstellungen = 'Einstellungen'#models.BinaryField(max_length=65000)
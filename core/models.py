from django.db import models


class Order(models.Model):
    external_id = models.IntegerField(unique=True)
    date = models.DateField()
    cost_usd = models.FloatField()
    cost_rub = models.FloatField()

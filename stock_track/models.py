from django.db import models
from django.utils import timezone

# Create your models here.

class Stocksmain(models.Model):
    exchange_name = models.CharField(max_length=50)
    st_name = models.CharField(max_length=255)
    st_code = models.CharField(max_length=50)
    st_buyprice = models.FloatField()
    st_targetprice = models.FloatField()
    st_stoploss = models.FloatField()
    st_ltp = models.FloatField()
    bought_on = models.DateField(default=timezone.now)
    user_id = models.IntegerField()
    last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        # get_latest_by = "bought_on"
        ordering = ('-bought_on', )
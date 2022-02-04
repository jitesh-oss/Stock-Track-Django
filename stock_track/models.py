from django.db import models
from django.utils import timezone

# Create your models here.

class Stocksmain(models.Model):
    exchange_name = models.CharField(max_length=50)
    st_type = models.CharField(max_length=50)
    st_name = models.CharField(max_length=255)
    st_code = models.CharField(max_length=50)
    st_position = models.CharField(max_length=50)
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

class Alertsmain(models.Model):
    al_exchange_name = models.CharField(max_length=50)
    al_type = models.CharField(max_length=50)
    al_name = models.CharField(max_length=255)
    al_code = models.CharField(max_length=50)
    al_triggerprice = models.FloatField()
    al_ltp = models.FloatField()
    al_condition = models.CharField(max_length=255)
    al_note = models.TextField()
    al_user_id = models.IntegerField()
    al_last_updated = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-al_last_updated', )

class Categorymain(models.Model):
    cat_name = models.CharField(max_length=50)
    cat_desc = models.CharField(max_length=255)
    cat_userid = models.TextField()
    cat_createdon = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-cat_createdon', )

class Journalmain(models.Model):
    jou_category = models.CharField(max_length=50)
    jou_exchange = models.CharField(max_length=50)
    jou_name = models.CharField(max_length=50)
    jou_position = models.CharField(max_length=50)
    jou_buydatetime = models.DateTimeField()
    jou_buyprice = models.FloatField()
    jou_buyqty = models.FloatField()
    jou_selldatetime = models.DateTimeField()
    jou_sellprice = models.FloatField()
    jou_sellqty = models.FloatField()
    jou_pl = models.FloatField()
    jou_status = models.CharField(max_length=50)
    jou_note = models.TextField()
    jou_catid = models.IntegerField()
    jou_userid = models.IntegerField()
    jou_createdon = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ('-jou_buydatetime', )
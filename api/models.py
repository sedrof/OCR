from django.db import models

# Create your models here.


class Invoice(models.Model):
    inv_ref = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=500)
    supplier_code = models.IntegerField(null=True)
    supplier_name = models.CharField(max_length=100)
    invoice_date = models.DateField(null=True, blank=True)
    due_date =models.DateField(null=True, blank=True)
    total_invoice_amount = models.FloatField(null=True)
    total_water_rate = models.FloatField(null=True)
    total_water_usage = models.FloatField(null=True)
    total_other_amount = models.FloatField(null=True)

    def __str__(self):
        return str(self.inv_ref)





class Meter(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='meters')
    meter_no = models.CharField(max_length=50,null=True)
    meter_type = models.CharField(max_length=50, null=True) 
    acc_description = models.CharField(max_length=250, null=True) 
    this_reading = models.IntegerField(null=True)
    last_reading = models.IntegerField(null=True)
    consumption = models.IntegerField(null=True)
    average_rate =  models.FloatField(null=True)
    other_rate = models.FloatField(null=True)
    consumption_period = models.DateField(null=True, blank=True)
    amount_from_inv = models.FloatField(null=True)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return str(self.meter_no)

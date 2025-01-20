from django.db import models
from django.utils import timezone

# Create your models here.


class Sponsor(models.Model):
    company_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    contact = models.CharField(max_length=10)
    amount = models.IntegerField()
    event = models.CharField(max_length=100)
    payment_success = models.BooleanField(default=False)
    date_added = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.company_name

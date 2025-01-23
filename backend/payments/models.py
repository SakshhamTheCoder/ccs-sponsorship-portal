from django.db import models
from django.utils import timezone


# Create your models here.
class Payment(models.Model):
    sponsor = models.ForeignKey(
        "sponsorship.Sponsor", on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.IntegerField()
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    payment_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.sponsor.company_name

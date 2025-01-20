from django.db import models


# Create your models here.
class Payment(models.Model):
    sponsor = models.OneToOneField(
        "sponsorship.Sponsor", on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.IntegerField()
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.sponsor.company_name

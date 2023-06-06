from django.db import models

class AwardWinner(models.Model):
    property_name = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    destination = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    class Meta:
        app_label = 'scraper'  # Specify the app_label for the model

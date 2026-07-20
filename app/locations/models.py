from django.db import models

class Country(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ua = models.CharField(max_length=100)
    flag_url = models.URLField(max_length=500, blank=True, null=True)
    phone_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ["name_en"]

    def __str__(self):
        return self.name_en


class City(models.Model):
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="cities"
    )
    name_en = models.CharField(max_length=150)
    name_ua = models.CharField(max_length=150)

    class Meta:
        unique_together = ("country", "name_en")
        ordering = ["name_en"]

    def __str__(self):
        return f"{self.name_en}, {self.country.name_en}"
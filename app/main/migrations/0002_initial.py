# Generated by Django 5.1.1 on 2024-10-08 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
        ('photo_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfolio',
            name='photos',
            field=models.ManyToManyField(blank=True, related_name='portfolios', to='photo_app.photo'),
        ),
    ]

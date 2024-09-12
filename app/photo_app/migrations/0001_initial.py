# Generated by Django 5.1.1 on 2024-09-07 18:27

import cloudinary.models
import photo_app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('title', models.CharField(blank=True, max_length=200, verbose_name='Title (optional)')),
                ('image', cloudinary.models.CloudinaryField(max_length=255, validators=[photo_app.models.file_validation], verbose_name='image')),
            ],
        ),
    ]

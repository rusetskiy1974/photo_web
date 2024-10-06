# Generated by Django 5.1.1 on 2024-10-02 13:38

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
                ('description', models.TextField(blank=True, null=True)),
                ('public_id', models.CharField(blank=True, max_length=255)),
            ],
        ),
    ]

# Generated by Django 4.0.3 on 2022-04-09 21:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userimage',
            name='owner',
        ),
    ]

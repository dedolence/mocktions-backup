# Generated by Django 3.2.7 on 2022-01-06 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0042_alter_bid_amount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testuser',
            name='watching',
        ),
        migrations.DeleteModel(
            name='TestListing',
        ),
        migrations.DeleteModel(
            name='TestUser',
        ),
    ]

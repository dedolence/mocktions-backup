# Generated by Django 3.2.7 on 2021-12-21 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0018_listing_current_bid'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='winning_bid',
            field=models.DecimalField(decimal_places=2, max_digits=6, null=True),
        ),
    ]

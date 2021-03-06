# Generated by Django 4.0.3 on 2022-04-26 15:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0012_alter_user_watchlist'),
    ]

    operations = [
        migrations.AddField(
            model_name='listing',
            name='draft',
            field=models.BooleanField(default=True, help_text='True = a posted listing; False = a temporary (draft) listing.'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='active',
            field=models.BooleanField(default=False, help_text='True = a posted listing; False = inactive (draft, expired, won, etc.).'),
        ),
    ]

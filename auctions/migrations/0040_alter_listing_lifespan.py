# Generated by Django 3.2.7 on 2022-01-06 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0039_listing_lifespan'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='lifespan',
            field=models.IntegerField(default=1, help_text='Days'),
        ),
    ]

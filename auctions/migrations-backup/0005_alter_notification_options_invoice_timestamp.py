# Generated by Django 4.0.3 on 2022-04-22 21:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_remove_invoice_items_listing_invoice_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['id']},
        ),
        migrations.AddField(
            model_name='invoice',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]

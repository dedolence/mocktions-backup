# Generated by Django 4.0.3 on 2022-04-22 21:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0006_alter_listing_invoice_alter_listing_winning_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='items', to='auctions.invoice'),
        ),
    ]

# Generated by Django 4.0.3 on 2022-04-22 21:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0005_alter_notification_options_invoice_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='items', to='auctions.invoice'),
        ),
        migrations.AlterField(
            model_name='listing',
            name='winning_user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='shopping_cart', to=settings.AUTH_USER_MODEL),
        ),
    ]
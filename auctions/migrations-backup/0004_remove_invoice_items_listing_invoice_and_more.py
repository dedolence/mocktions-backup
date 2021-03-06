# Generated by Django 4.0.3 on 2022-04-20 20:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_invoice_items'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='items',
        ),
        migrations.AddField(
            model_name='listing',
            name='invoice',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='auctions.invoice'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
    ]

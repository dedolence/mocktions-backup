# Generated by Django 4.0.3 on 2022-04-14 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_alter_comment_replyto'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='replyTo',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET(1), to='auctions.comment'),
        ),
    ]
# Generated by Django 4.0.3 on 2022-04-09 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0003_alter_user_profile_picture'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='profile_picture',
        ),
    ]

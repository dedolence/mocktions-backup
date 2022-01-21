# Generated by Django 3.2.7 on 2022-01-21 21:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0013_alter_user_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_picture',
            field=models.CharField(blank=True, default='/static/images/user_avatar.png', max_length=100, null=True),
        ),
    ]

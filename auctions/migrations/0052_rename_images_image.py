# Generated by Django 3.2.7 on 2022-01-14 22:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0051_alter_images_image'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Images',
            new_name='Image',
        ),
    ]
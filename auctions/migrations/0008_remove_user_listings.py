# Generated by Django 4.1.4 on 2022-12-13 14:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0007_user_listings'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='listings',
        ),
    ]

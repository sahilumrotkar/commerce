# Generated by Django 3.2.5 on 2021-08-05 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0004_auctionitem_closing_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionitem',
            name='last_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]

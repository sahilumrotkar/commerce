# Generated by Django 3.2.5 on 2021-07-30 04:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auto_20210729_0554'),
    ]

    operations = [
        migrations.AddField(
            model_name='bid',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

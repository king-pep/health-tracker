# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-12-11 18:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entries', '0015_physicalactivity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalactivity',
            name='name',
            field=models.TextField(db_index=True, max_length=255),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-07-15 16:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0002_auto_20180715_1356'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='get_out',
            field=models.DateTimeField(null=True),
        ),
    ]

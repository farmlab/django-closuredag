# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-20 12:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dag', '0003_closure'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='closure',
            name='name',
        ),
    ]

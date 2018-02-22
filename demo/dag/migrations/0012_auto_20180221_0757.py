# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-02-21 07:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dag', '0011_auto_20180221_0754'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='node',
            name='direct_edge',
        ),
        migrations.RemoveField(
            model_name='node',
            name='entry_edge',
        ),
        migrations.RemoveField(
            model_name='node',
            name='exit_edge',
        ),
        migrations.RemoveField(
            model_name='node',
            name='hops',
        ),
        migrations.AddField(
            model_name='relation',
            name='direct_edge',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='directs_edges', to='dag.Relation'),
        ),
        migrations.AddField(
            model_name='relation',
            name='entry_edge',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='entries_edges', to='dag.Relation'),
        ),
        migrations.AddField(
            model_name='relation',
            name='exit_edge',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='exits_edges', to='dag.Relation'),
        ),
        migrations.AddField(
            model_name='relation',
            name='hops',
            field=models.IntegerField(default=0),
        ),
    ]

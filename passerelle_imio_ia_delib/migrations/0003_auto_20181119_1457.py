# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-11-19 13:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passerelle_imio_ia_delib', '0002_auto_20170921_1213'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iimioiadelib',
            name='log_level',
        ),
        migrations.AlterField(
            model_name='iimioiadelib',
            name='description',
            field=models.TextField(verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='iimioiadelib',
            name='title',
            field=models.CharField(max_length=50, verbose_name='Title'),
        ),
    ]

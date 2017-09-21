# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passerelle_imio_ia_delib', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iimioiadelib',
            name='slug',
            field=models.SlugField(unique=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_resourcelog'),
    ]

    operations = [
        migrations.CreateModel(
            name='IImioIaDelib',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField()),
                ('description', models.TextField()),
                ('log_level', models.CharField(default=b'INFO', max_length=10, verbose_name='Log Level', choices=[(b'NOTSET', b'NOTSET'), (b'DEBUG', b'DEBUG'), (b'INFO', b'INFO'), (b'WARNING', b'WARNING'), (b'ERROR', b'ERROR'), (b'CRITICAL', b'CRITICAL'), (b'FATAL', b'FATAL')])),
                ('wsdl_url', models.CharField(help_text='WSDL URL', max_length=128, verbose_name='WSDL URL')),
                ('verify_cert', models.BooleanField(default=True, verbose_name='Check HTTPS Certificate validity')),
                ('username', models.CharField(max_length=128, verbose_name='Username', blank=True)),
                ('password', models.CharField(max_length=128, verbose_name='Password', blank=True)),
                ('keystore', models.FileField(help_text='Certificate and private key in PEM format', upload_to=b'iparapheur', null=True, verbose_name='Keystore', blank=True)),
                ('users', models.ManyToManyField(to='base.ApiUser', blank=True)),
            ],
            options={
                'verbose_name': 'i-ImioIaDelib',
            },
        ),
    ]

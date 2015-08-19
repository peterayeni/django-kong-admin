# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0003_auto_20150819_0643'),
    ]

    operations = [
        migrations.CreateModel(
            name='OAuth2Reference',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('redirect_uri', models.URLField()),
                ('client_id', models.CharField(null=True, max_length=64, unique=True, blank=True)),
                ('client_secret', models.TextField(null=True, blank=True)),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name': 'OAuth2 Reference',
                'verbose_name_plural': 'OAuth2 References',
            },
        ),
    ]

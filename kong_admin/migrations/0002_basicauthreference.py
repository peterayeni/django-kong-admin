# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicAuthReference',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, blank=True, verbose_name='synchronized', editable=False)),
                ('username', models.CharField(null=True, blank=True, unique=True, max_length=32)),
                ('password', models.CharField(null=True, blank=True, unique=True, max_length=40)),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name': 'Basic Auth Entity',
                'verbose_name_plural': 'Basic Auth Entities',
            },
        ),
    ]

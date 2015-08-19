# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0008_auto_20150819_0731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauth2application',
            name='consumers',
            field=models.ManyToManyField(blank=True, null=True, to='kong_admin.ConsumerReference', related_name='oauth2'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0007_auto_20150819_0723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='oauth2application',
            name='consumers',
            field=models.ManyToManyField(to='kong_admin.ConsumerReference', null=True),
        ),
    ]

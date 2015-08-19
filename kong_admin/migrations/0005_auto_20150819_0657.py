# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0004_oauth2reference'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='oauth2reference',
            name='consumer',
        ),
        migrations.AddField(
            model_name='oauth2reference',
            name='consumers',
            field=models.ManyToManyField(to='kong_admin.ConsumerReference'),
        ),
    ]

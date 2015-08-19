# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0005_auto_20150819_0657'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='OAuth2Reference',
            new_name='OAuth2ApplicationReference',
        ),
        migrations.AlterModelOptions(
            name='oauth2applicationreference',
            options={'verbose_name_plural': 'OAuth2 Application References', 'verbose_name': 'OAuth2 Application Reference'},
        ),
    ]

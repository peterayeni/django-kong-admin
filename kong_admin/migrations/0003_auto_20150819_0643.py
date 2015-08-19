# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0002_basicauthreference'),
    ]

    operations = [
        migrations.CreateModel(
            name='KeyAuthReference',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, null=True, verbose_name='synchronized', blank=True)),
                ('key', models.TextField()),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name': 'Key Auth Reference',
                'verbose_name_plural': 'Key Auth References',
            },
        ),
        migrations.AlterModelOptions(
            name='basicauthreference',
            options={'verbose_name': 'Basic Auth Reference', 'verbose_name_plural': 'Basic Auth References'},
        ),
    ]

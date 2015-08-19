# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0006_auto_20150819_0700'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicAuthSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('username', models.CharField(blank=True, max_length=32, unique=True, null=True)),
                ('password', models.CharField(blank=True, max_length=40, unique=True, null=True)),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'Basic Auth Settings',
                'verbose_name': 'Basic Auth Setting',
            },
        ),
        migrations.CreateModel(
            name='KeyAuthSetting',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('key', models.TextField()),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'Key Auth Settings',
                'verbose_name': 'Key Auth Setting',
            },
        ),
        migrations.CreateModel(
            name='OAuth2Application',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('redirect_uri', models.URLField()),
                ('client_id', models.CharField(blank=True, max_length=64, unique=True, null=True)),
                ('client_secret', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('consumers', models.ManyToManyField(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'OAuth2 Application',
                'verbose_name': 'OAuth2 Application',
            },
        ),
        migrations.RemoveField(
            model_name='basicauthreference',
            name='consumer',
        ),
        migrations.RemoveField(
            model_name='keyauthreference',
            name='consumer',
        ),
        migrations.RemoveField(
            model_name='oauth2applicationreference',
            name='consumers',
        ),
        migrations.DeleteModel(
            name='BasicAuthReference',
        ),
        migrations.DeleteModel(
            name='KeyAuthReference',
        ),
        migrations.DeleteModel(
            name='OAuth2ApplicationReference',
        ),
    ]

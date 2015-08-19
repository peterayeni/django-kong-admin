# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kong_admin', '0009_auto_20150819_0741'),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicAuthReference',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, verbose_name='synchronized', editable=False, blank=True)),
                ('username', models.CharField(null=True, max_length=32, unique=True, blank=True)),
                ('password', models.CharField(null=True, max_length=40, unique=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'Basic Auth References',
                'verbose_name': 'Basic Auth Reference',
            },
        ),
        migrations.CreateModel(
            name='KeyAuthReference',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, verbose_name='synchronized', editable=False, blank=True)),
                ('key', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Key Auth References',
                'verbose_name': 'Key Auth Reference',
            },
        ),
        migrations.CreateModel(
            name='OAuth2Reference',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(verbose_name='updated', auto_now=True)),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, verbose_name='synchronized', editable=False, blank=True)),
                ('name', models.CharField(max_length=32, unique=True)),
                ('redirect_uri', models.URLField()),
                ('client_id', models.CharField(null=True, max_length=64, unique=True, blank=True)),
                ('client_secret', models.TextField(null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'OAuth2 References',
                'verbose_name': 'OAuth2 Reference',
            },
        ),
        migrations.RemoveField(
            model_name='basicauthsetting',
            name='consumer',
        ),
        migrations.RemoveField(
            model_name='keyauthsetting',
            name='consumer',
        ),
        migrations.RemoveField(
            model_name='oauth2application',
            name='consumers',
        ),
        migrations.RenameField(
            model_name='apireference',
            old_name='api_id',
            new_name='kong_id',
        ),
        migrations.RenameField(
            model_name='consumerreference',
            old_name='consumer_id',
            new_name='kong_id',
        ),
        migrations.RenameField(
            model_name='pluginconfigurationreference',
            old_name='plugin_configuration_id',
            new_name='kong_id',
        ),
        migrations.DeleteModel(
            name='BasicAuthSetting',
        ),
        migrations.DeleteModel(
            name='KeyAuthSetting',
        ),
        migrations.DeleteModel(
            name='OAuth2Application',
        ),
        migrations.AddField(
            model_name='oauth2reference',
            name='consumer',
            field=models.ForeignKey(to='kong_admin.ConsumerReference'),
        ),
        migrations.AddField(
            model_name='keyauthreference',
            name='consumer',
            field=models.ForeignKey(to='kong_admin.ConsumerReference'),
        ),
        migrations.AddField(
            model_name='basicauthreference',
            name='consumer',
            field=models.ForeignKey(to='kong_admin.ConsumerReference'),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIReference',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('target_url', models.URLField()),
                ('name', models.CharField(unique=True, max_length=32, null=True, blank=True)),
                ('public_dns', models.CharField(unique=True, max_length=32, null=True, blank=True)),
                ('path', models.CharField(max_length=32, null=True, blank=True)),
                ('strip_path', models.BooleanField(default=False)),
                ('api_id', models.UUIDField(editable=False, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'API Reference',
                'verbose_name_plural': 'API References',
            },
        ),
        migrations.CreateModel(
            name='ConsumerReference',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('consumer_id', models.UUIDField(editable=False, null=True, blank=True)),
                ('username', models.CharField(unique=True, max_length=32, null=True, blank=True)),
                ('custom_id', models.CharField(unique=True, max_length=48, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Consumer Reference',
                'verbose_name_plural': 'Consumer References',
            },
        ),
        migrations.CreateModel(
            name='PluginConfigurationField',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('property', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name': 'Plugin Configuration Field',
                'verbose_name_plural': 'Plugin Configuration Fields',
            },
        ),
        migrations.CreateModel(
            name='PluginConfigurationReference',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='created', auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('plugin_configuration_id', models.UUIDField(editable=False, null=True, blank=True)),
                ('name', models.CharField(choices=[('basicauth', 'basicauth'), ('cors', 'cors'), ('filelog', 'filelog'), ('httplog', 'httplog'), ('keyauth', 'keyauth'), ('oauth2', 'oauth2'), ('ratelimiting', 'ratelimiting'), ('request_transformer', 'request_transformer'), ('requestsizelimiting', 'requestsizelimiting'), ('response_transformer', 'response_transformer'), ('ssl', 'ssl'), ('tcplog', 'tcplog'), ('udplog', 'udplog')], verbose_name='Plugin Name', max_length=32)),
                ('enabled', models.BooleanField(default=True)),
                ('api', models.ForeignKey(to='kong_admin.APIReference', related_name='plugins')),
                ('consumer', models.ForeignKey(null=True, to='kong_admin.ConsumerReference', related_name='plugins', blank=True)),
            ],
            options={
                'verbose_name': 'Plugin Configuration Reference',
                'verbose_name_plural': 'Plugin Configuration References',
            },
        ),
        migrations.AddField(
            model_name='pluginconfigurationfield',
            name='configuration',
            field=models.ForeignKey(to='kong_admin.PluginConfigurationReference', related_name='fields'),
        ),
        migrations.AlterUniqueTogether(
            name='pluginconfigurationreference',
            unique_together=set([('name', 'api')]),
        ),
    ]

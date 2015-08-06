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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('target_url', models.URLField()),
                ('name', models.CharField(max_length=32, unique=True, null=True, blank=True)),
                ('public_dns', models.CharField(max_length=32, unique=True, null=True, blank=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('consumer_id', models.UUIDField(editable=False, null=True, blank=True)),
                ('username', models.CharField(max_length=32, unique=True, null=True, blank=True)),
                ('custom_id', models.CharField(max_length=48, unique=True, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'Consumer Reference',
                'verbose_name_plural': 'Consumer References',
            },
        ),
        migrations.CreateModel(
            name='PluginConfigurationField',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(editable=False, verbose_name='synchronized', null=True, blank=True)),
                ('plugin_configuration_id', models.UUIDField(editable=False, null=True, blank=True)),
                ('name', models.CharField(max_length=32, verbose_name='Plugin Name', choices=[('basicauth', 'basicauth'), ('cors', 'cors'), ('filelog', 'filelog'), ('httplog', 'httplog'), ('keyauth', 'keyauth'), ('oauth2', 'oauth2'), ('ratelimiting', 'ratelimiting'), ('request_transformer', 'request_transformer'), ('requestsizelimiting', 'requestsizelimiting'), ('response_transformer', 'response_transformer'), ('ssl', 'ssl'), ('tcplog', 'tcplog'), ('udplog', 'udplog')])),
                ('enabled', models.BooleanField(default=True)),
                ('api', models.ForeignKey(related_name='plugins', to='kong_admin.APIReference')),
                ('consumer', models.ForeignKey(related_name='plugins', null=True, blank=True, to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name': 'Plugin Configuration Reference',
                'verbose_name_plural': 'Plugin Configuration References',
            },
        ),
        migrations.AddField(
            model_name='pluginconfigurationfield',
            name='configuration',
            field=models.ForeignKey(related_name='fields', to='kong_admin.PluginConfigurationReference'),
        ),
        migrations.AlterUniqueTogether(
            name='pluginconfigurationreference',
            unique_together=set([('name', 'api')]),
        ),
    ]

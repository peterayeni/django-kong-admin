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
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, editable=False, blank=True, verbose_name='synchronized')),
                ('target_url', models.URLField()),
                ('name', models.CharField(null=True, unique=True, default=None, max_length=32, blank=True)),
                ('public_dns', models.CharField(null=True, unique=True, default=None, max_length=32, blank=True)),
                ('path', models.CharField(null=True, default=None, max_length=32, blank=True)),
                ('strip_path', models.BooleanField(default=False)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'API References',
                'verbose_name': 'API Reference',
            },
        ),
        migrations.CreateModel(
            name='BasicAuthReference',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, editable=False, blank=True, verbose_name='synchronized')),
                ('username', models.CharField(max_length=32, unique=True)),
                ('password', models.CharField(max_length=40)),
            ],
            options={
                'verbose_name_plural': 'Basic Auth References',
                'verbose_name': 'Basic Auth Reference',
            },
        ),
        migrations.CreateModel(
            name='ConsumerReference',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, editable=False, blank=True, verbose_name='synchronized')),
                ('username', models.CharField(null=True, blank=True, max_length=32, unique=True)),
                ('custom_id', models.CharField(null=True, blank=True, max_length=48, unique=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Consumer References',
                'verbose_name': 'Consumer Reference',
            },
        ),
        migrations.CreateModel(
            name='KeyAuthReference',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, editable=False, blank=True, verbose_name='synchronized')),
                ('key', models.TextField()),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'Key Auth References',
                'verbose_name': 'Key Auth Reference',
            },
        ),
        migrations.CreateModel(
            name='OAuth2Reference',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, editable=False, blank=True, verbose_name='synchronized')),
                ('name', models.CharField(max_length=32, unique=True)),
                ('redirect_uri', models.URLField()),
                ('client_id', models.CharField(null=True, blank=True, max_length=64, unique=True)),
                ('client_secret', models.TextField(null=True, blank=True)),
                ('consumer', models.ForeignKey(to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'OAuth2 References',
                'verbose_name': 'OAuth2 Reference',
            },
        ),
        migrations.CreateModel(
            name='PluginConfigurationField',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('property', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=32)),
            ],
            options={
                'verbose_name_plural': 'Plugin Configuration Fields',
                'verbose_name': 'Plugin Configuration Field',
            },
        ),
        migrations.CreateModel(
            name='PluginConfigurationReference',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('kong_id', models.UUIDField(null=True, editable=False, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated')),
                ('synchronized', models.BooleanField(default=False)),
                ('synchronized_at', models.DateTimeField(null=True, editable=False, blank=True, verbose_name='synchronized')),
                ('name', models.CharField(choices=[('basicauth', 'basicauth'), ('cors', 'cors'), ('filelog', 'filelog'), ('httplog', 'httplog'), ('keyauth', 'keyauth'), ('oauth2', 'oauth2'), ('ratelimiting', 'ratelimiting'), ('request_transformer', 'request_transformer'), ('requestsizelimiting', 'requestsizelimiting'), ('response_transformer', 'response_transformer'), ('ssl', 'ssl'), ('tcplog', 'tcplog'), ('udplog', 'udplog')], max_length=32, verbose_name='Plugin Name')),
                ('enabled', models.BooleanField(default=True)),
                ('api', models.ForeignKey(related_name='plugins', to='kong_admin.APIReference')),
                ('consumer', models.ForeignKey(related_name='plugins', blank=True, null=True, to='kong_admin.ConsumerReference')),
            ],
            options={
                'verbose_name_plural': 'Plugin Configuration References',
                'verbose_name': 'Plugin Configuration Reference',
            },
        ),
        migrations.AddField(
            model_name='pluginconfigurationfield',
            name='configuration',
            field=models.ForeignKey(related_name='fields', to='kong_admin.PluginConfigurationReference'),
        ),
        migrations.AddField(
            model_name='basicauthreference',
            name='consumer',
            field=models.ForeignKey(to='kong_admin.ConsumerReference'),
        ),
        migrations.AlterUniqueTogether(
            name='pluginconfigurationreference',
            unique_together=set([('name', 'api')]),
        ),
    ]

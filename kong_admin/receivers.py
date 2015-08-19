# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from contextlib import closing

from django.db.models.signals import pre_save, pre_delete
from django.dispatch.dispatcher import receiver

from .models import APIReference, ConsumerReference, BasicAuthReference, KeyAuthReference, OAuth2Reference, \
    PluginConfigurationReference
from .factory import get_kong_client, get_api_sync_engine, get_consumer_sync_engine


@receiver(pre_save, sender=APIReference)
def before_saving_api(sender, instance, **kwargs):
    instance.synchronized = False


@receiver(pre_delete, sender=APIReference)
def before_delete_api(sender, instance, **kwargs):
    with closing(get_kong_client()) as client:
        get_api_sync_engine().withdraw(client, instance)


@receiver(pre_save, sender=ConsumerReference)
def before_saving_consumer(sender, instance, **kwargs):
    instance.synchronized = False


@receiver(pre_delete, sender=ConsumerReference)
def before_delete_consumer(sender, instance, **kwargs):
    with closing(get_kong_client()) as client:
        get_consumer_sync_engine().withdraw(client, instance)


@receiver(pre_save, sender=BasicAuthReference)
def before_saving_basic_auth(sender, instance, **kwargs):
    """
    We synchronize BasicAuthReference objects together with the consumer
    """
    instance.synchronized = False
    ConsumerReference.objects.filter(id=instance.consumer.id, synchronized=True).update(synchronized=False)


@receiver(pre_save, sender=KeyAuthReference)
def before_saving_key_auth(sender, instance, **kwargs):
    """
    We synchronize KeyAuthReference objects together with the consumer
    """
    instance.synchronized = False
    ConsumerReference.objects.filter(id=instance.consumer.id, synchronized=True).update(synchronized=False)


@receiver(pre_save, sender=OAuth2Reference)
def before_saving_oauth(sender, instance, **kwargs):
    """
    We synchronize OAuth2Reference objects together with the consumer
    """
    instance.synchronized = False
    ConsumerReference.objects.filter(id=instance.consumer.id, synchronized=True).update(synchronized=False)


@receiver(pre_save, sender=PluginConfigurationReference)
def before_saving_plugin_configuration(sender, instance, **kwargs):
    instance.synchronized = False


@receiver(pre_delete, sender=PluginConfigurationReference)
def before_delete_plugin_configuration(sender, instance, **kwargs):
    with closing(get_kong_client()) as client:
        get_api_sync_engine().plugins().withdraw(client, instance)

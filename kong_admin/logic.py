# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from .factory import get_api_sync_engine, get_consumer_sync_engine
from .models import APIReference, ConsumerReference, PluginConfigurationReference


def synchronize_apis(client, queryset=None):
    return get_api_sync_engine().synchronize(client, queryset=queryset, delete=True)


def synchronize_api(client, obj, toggle=False):
    if (toggle and obj.enabled) or (not toggle and not obj.enabled):
        obj = get_api_sync_engine().withdraw(client, obj)
        obj.enabled = False
    else:
        obj = get_api_sync_engine().publish(client, obj)
        obj.enabled = True

    if toggle:
        # Updated enabled state without triggering another save
        APIReference.objects.filter(id=obj.id).update(enabled=obj.enabled)

    return obj

def synchronize_plugin_configurations(client, queryset=None):
    return get_api_sync_engine().plugins().synchronize(client, queryset=queryset, delete=True)


def synchronize_plugin_configuration(client, obj, toggle=False):
    obj.enabled = not obj.enabled if toggle else obj.enabled
    obj = get_api_sync_engine().plugins().publish(client, obj)

    # Updated enabled state without triggering another save
    PluginConfigurationReference.objects.filter(id=obj.id).update(enabled=obj.enabled)

    return obj


def synchronize_consumers(client, queryset=None):
    return get_consumer_sync_engine().synchronize(client, queryset=queryset, delete=True)


def synchronize_consumer(client, obj, toggle=False):
    if (toggle and obj.enabled) or (not toggle and not obj.enabled):
        obj = get_consumer_sync_engine().withdraw(client, obj)
        obj.enabled = False
    else:
        obj = get_consumer_sync_engine().publish(client, obj)
        obj.enabled = True

    if toggle:
        # Updated enabled state without triggering another save
        ConsumerReference.objects.filter(id=obj.id).update(enabled=obj.enabled)

    return obj

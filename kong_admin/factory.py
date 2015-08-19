# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.conf import settings
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string

from .sync.apis import APISyncEngine
from .sync.consumers import ConsumerSyncEngine


def get_api_sync_engine():
    return APISyncEngine()


def get_consumer_sync_engine():
    return ConsumerSyncEngine()


def get_kong_client():
    from kong.client import KongAdminClient
    from kong.simulator import KongAdminSimulator

    api_url = getattr(settings, 'KONG_ADMIN_URL')
    simulator_enabled = getattr(settings, 'KONG_ADMIN_SIMULATOR')

    if simulator_enabled is True:
        return KongAdminSimulator(api_url)

    return KongAdminClient(api_url)

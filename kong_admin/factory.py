# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from django.conf import settings
from django.utils.lru_cache import lru_cache
from django.utils.module_loading import import_string


def create_kong_client():
    from kong.client import KongAdminClient
    from kong.simulator import KongAdminSimulator

    api_url = getattr(settings, 'KONG_ADMIN_URL')
    simulator_enabled = getattr(settings, 'KONG_ADMIN_SIMULATOR')

    if simulator_enabled is True:
        return KongAdminSimulator(api_url)

    return KongAdminClient(api_url)

@lru_cache(1)
def get_api_sync_engine():
    sync_engine_class_name = getattr(settings, 'KONG_ADMIN_API_SYNCHRONIZATION_ENGINE')
    sync_engine_class = import_string(sync_engine_class_name)
    return sync_engine_class(create_kong_client())


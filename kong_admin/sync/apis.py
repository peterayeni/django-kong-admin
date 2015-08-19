# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from kong.exceptions import ConflictError
from kong_admin.models import APIReference, PluginConfigurationReference, PluginConfigurationField

from .base import KongProxySyncEngine


class APISyncEngine(KongProxySyncEngine):
    def plugins(self):
        return PluginConfigurationSyncEngine()

    def get_proxy_class(self):
        return APIReference

    def on_retrieve_all(self, client):
        apis = list(client.apis.iterate())
        for api_struct in apis:
            yield api_struct

    def is_published(self, client, kong_id, parent_kong_id=None):
        try:
            result = client.apis.retrieve(str(kong_id))
        except ValueError:
            return False
        return result is not None

    def on_publish(self, client, obj):
        try:
            api_struct = client.apis.add_or_update(
                api_id=obj.kong_id, target_url=obj.target_url, name=obj.name, public_dns=obj.public_dns,
                path=obj.path, strip_path=obj.strip_path)
        except ConflictError:
            api_struct = client.apis.update(
                name_or_id=(obj.name or obj.public_dns), target_url=obj.target_url, name=obj.name,
                public_dns=obj.public_dns, path=obj.path, strip_path=obj.strip_path)
        return api_struct['id']

    def on_withdraw_by_id(self, client, kong_id, parent_kong_id=None):
        client.apis.delete(str(kong_id))


class PluginConfigurationSyncEngine(KongProxySyncEngine):
    def get_proxy_class(self):
        return PluginConfigurationReference

    def on_retrieve_all(self, client):
        apis = list(client.apis.iterate())
        for api_struct in apis:
            api_kong_id = api_struct.get('id', None)
            assert api_kong_id is not None

            plugin_configurations = client.apis.plugins(api_kong_id).list(size=100).get('data', None)
            assert plugin_configurations is not None
            for plugin_configuration_struct in plugin_configurations:
                yield plugin_configuration_struct

    def is_published(self, client, kong_id, parent_kong_id=None):
        try:
            result = client.apis.plugins(str(parent_kong_id)).retrieve(str(kong_id))
        except ValueError:
            return False
        return result is not None

    def get_parent_object(self, obj):
        return obj.api

    def get_parent_key(self):
        return 'api_id'

    def on_publish(self, client, obj):
        fields = {}

        for field in PluginConfigurationField.objects.filter(configuration=obj):
            fields[field.property] = field.value

        api_kong_id = obj.api.kong_id
        consumer_kong_id = obj.consumer.kong_id if obj.consumer is not None else None

        try:
            plugin_configuration_struct = client.apis.plugins(str(api_kong_id)).create_or_update(
                plugin_configuration_id=obj.kong_id, plugin_name=obj.name, enabled=obj.enabled,
                consumer_id=consumer_kong_id, **fields)
        except ConflictError:
            plugin_configuration_struct = client.apis.plugins(str(api_kong_id)).update(
                plugin_name=obj.name, enabled=obj.enabled, consumer_id=consumer_kong_id, **fields)

        return plugin_configuration_struct['id']

    def on_withdraw_by_id(self, client, kong_id, parent_kong_id=None):
        assert kong_id is not None
        assert parent_kong_id is not None

        client.apis.plugins(parent_kong_id).delete(kong_id)

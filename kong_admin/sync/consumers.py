# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from abc import ABCMeta, abstractmethod

from kong.exceptions import ConflictError
from kong_admin.models import ConsumerReference, BasicAuthReference

from .base import KongProxySyncEngine


class ConsumerSyncEngine(KongProxySyncEngine):
    def basic_auth(self):
        return BasicAuthSyncEngine()

    def get_proxy_class(self):
        return ConsumerReference

    def on_retrieve_all(self, client):
        consumers = list(client.consumers.iterate())
        for consumer_struct in consumers:
            yield consumer_struct

    def is_published(self, client, kong_id, parent_kong_id=None):
        try:
            result = client.consumers.retrieve(str(kong_id))
        except ValueError:
            return False
        return result is not None

    def on_publish(self, client, obj):
        try:
            consumer_struct = client.consumers.create_or_update(
                consumer_id=obj.kong_id, username=obj.username, custom_id=obj.custom_id)
        except ConflictError:
            consumer_struct = client.consumers.update(
                username_or_id=(obj.username or obj.kong_id), username=obj.username, custom_id=obj.custom_id)
        return consumer_struct['id']

    def on_withdraw_by_id(self, client, kong_id, parent_kong_id=None):
         client.consumers.delete(str(kong_id))

    def after_publish(self, client, obj):
        for basic_auth in BasicAuthReference.objects.filter(consumer=obj):
            self.basic_auth().publish(client, basic_auth)
        return super(ConsumerSyncEngine, self).after_publish(client, obj)

    def before_withdraw(self, client, obj):
        for basic_auth in BasicAuthReference.objects.filter(consumer=obj):
            self.basic_auth().withdraw(client, basic_auth)
        return super(ConsumerSyncEngine, self).before_withdraw(client, obj)


class ConsumerAuthSyncEngine(KongProxySyncEngine):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_auth_client(self, client, consumer_kong_id):
        """
        Returns the authentication client to use
        """

    def on_retrieve_all(self, client):
        consumers = list(client.consumers.iterate())
        for consumer_struct in consumers:
            consumer_kong_id = consumer_struct.get('id', None)
            assert consumer_kong_id is not None

            auth_list = self.get_auth_client(client, consumer_kong_id).list(size=100).get('data', None)
            assert auth_list is not None
            for auth_struct in auth_list:
                yield auth_struct

    def is_published(self, client, kong_id, parent_kong_id=None):
        try:
            result = self.get_auth_client(client, parent_kong_id).retrieve(str(kong_id))
        except ValueError:
            return False
        return result is not None

    def get_parent_object(self, obj):
        return obj.consumer

    def get_parent_key(self):
        return 'consumer_id'

    def on_withdraw_by_id(self, client, kong_id, parent_kong_id=None):
        assert kong_id is not None
        assert parent_kong_id is not None

        self.get_auth_client(client, parent_kong_id).delete(kong_id)


class BasicAuthSyncEngine(ConsumerAuthSyncEngine):
    def get_proxy_class(self):
        return BasicAuthReference

    def get_auth_client(self, client, consumer_kong_id):
        return client.consumers.basic_auth(str(consumer_kong_id))

    def on_publish(self, client, obj):
        auth_struct = self.get_auth_client(client, obj.consumer.kong_id).create_or_update(
            basic_auth_id=obj.kong_id, username=obj.username, password=obj.password)

        return auth_struct['id']

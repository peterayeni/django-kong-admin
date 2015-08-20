# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import uuid
from abc import ABCMeta, abstractmethod

from kong.exceptions import ConflictError
from kong_admin.models import ConsumerReference, BasicAuthReference, KeyAuthReference, OAuth2Reference

from .base import KongProxySyncEngine


class ConsumerSyncEngine(KongProxySyncEngine):
    def basic_auth(self):
        return BasicAuthSyncEngine()

    def key_auth(self):
        return KeyAuthSyncEngine()

    def oauth2(self):
        return OAuth2SyncEngine()

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
        """
        :param client: The client to interface with kong with
        :type client: kong.contract.KongAdminContract
        :param obj: The KongProxyModel to work with
        :type obj: kong_admin.models.ConsumerReference
        :rtype: uuid.UUID
        :return: The uuid of the entity that has been published
        """
        try:
            consumer_struct = client.consumers.create_or_update(
                consumer_id=obj.kong_id, username=obj.username, custom_id=obj.custom_id)
        except ConflictError:
            consumer_struct = client.consumers.update(
                username_or_id=(obj.username or obj.kong_id), username=obj.username, custom_id=obj.custom_id)
        return uuid.UUID(consumer_struct['id'])

    def on_withdraw_by_id(self, client, kong_id, parent_kong_id=None):
         client.consumers.delete(str(kong_id))

    def after_publish(self, client, obj):
        self.basic_auth().synchronize(client, BasicAuthReference.objects.filter(consumer=obj), delete=True)
        self.key_auth().synchronize(client, KeyAuthReference.objects.filter(consumer=obj), delete=True)
        self.oauth2().synchronize(client, OAuth2Reference.objects.filter(consumer=obj), delete=True)
        super(ConsumerSyncEngine, self).after_publish(client, obj)

    def before_withdraw(self, client, obj):
        for oauth2 in OAuth2Reference.objects.filter(consumer=obj):
            self.oauth2().withdraw(client, oauth2)
        for key_auth in KeyAuthReference.objects.filter(consumer=obj):
            self.key_auth().withdraw(client, key_auth)
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
        """
        :param client: The client to interface with kong with
        :type client: kong.contract.KongAdminContract
        :param obj: The KongProxyModel to work with
        :type obj: kong_admin.models.BasicAuthReference
        :rtype: uuid.UUID
        :return: The uuid of the entity that has been published
        """
        auth_struct = self.get_auth_client(client, obj.consumer.kong_id).create_or_update(
            basic_auth_id=obj.kong_id, username=obj.username, password=obj.password)
        return uuid.UUID(auth_struct['id'])


class KeyAuthSyncEngine(ConsumerAuthSyncEngine):
    def get_proxy_class(self):
        return KeyAuthReference

    def get_auth_client(self, client, consumer_kong_id):
        return client.consumers.key_auth(str(consumer_kong_id))

    def on_publish(self, client, obj):
        """
        :param client: The client to interface with kong with
        :type client: kong.contract.KongAdminContract
        :param obj: The KongProxyModel to work with
        :type obj: kong_admin.models.KeyAuthReference
        :rtype: uuid.UUID
        :return: The uuid of the entity that has been published
        """
        auth_struct = self.get_auth_client(client, obj.consumer.kong_id).create_or_update(
            key_auth_id=obj.kong_id, key=obj.key)
        return uuid.UUID(auth_struct['id'])


class OAuth2SyncEngine(ConsumerAuthSyncEngine):
    def get_proxy_class(self):
        return OAuth2Reference

    def get_auth_client(self, client, consumer_kong_id):
        return client.consumers.oauth2(str(consumer_kong_id))

    def on_publish(self, client, obj):
        """
        :param client: The client to interface with kong with
        :type client: kong.contract.KongAdminContract
        :param obj: The KongProxyModel to work with
        :type obj: kong_admin.models.OAuth2Reference
        :rtype: uuid.UUID
        :return: The uuid of the entity that has been published
        """
        auth_struct = self.get_auth_client(client, obj.consumer.kong_id).create_or_update(
            oauth2_id=obj.kong_id, name=obj.name, redirect_uri=obj.redirect_uri, client_id=obj.client_id,
            client_secret=obj.client_secret)

        client_id = auth_struct['client_id']
        client_secret = auth_struct['client_secret']

        if obj.client_id != client_id or obj.client_secret != client_secret:
            obj.client_id = client_id
            obj.client_secret = client_secret
            self.get_proxy_class().objects.filter(id=obj.id).update(
                client_id=obj.client_id, client_secret=obj.client_secret)

        return uuid.UUID(auth_struct['id'])

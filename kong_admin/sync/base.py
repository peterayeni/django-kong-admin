# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging

from django.db import transaction
from django.utils import timezone

from six import with_metaclass
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class KongProxySyncEngine(with_metaclass(ABCMeta, object)):
    @abstractmethod
    def get_proxy_class(self):
        """
        :return: Returns the actual class of the KongProxyModel were working with
        """

    @abstractmethod
    def on_retrieve_all(self, client):
        """
        Called to retrieve all objects from kong

        :param client:
        :type client: kong.contract.KongAdminContract
        :return: collections.Iterable
        """

    @abstractmethod
    def is_published(self, client, kong_id, parent_kong_id=None):
        """
        Caleld to check whether an object is known at kong

        :param client:
        :param kong_id:
        :param parent_kong_id:
        :return:
        """

    @abstractmethod
    def on_publish(self, client, obj):
        """
        Called to publish a KongProxyModel to Kong

        :param client:
        :type client: kong.contract.KongAdminContract
        :param obj:
        :type obj: kong_admin.models.KongProxyModel
        :rtype: uuid.UUID
        :return: The uuid of the newly published object
        """

    @abstractmethod
    def on_withdraw_by_id(self, client, kong_id, parent_kong_id=None):
        """
        Called to withdraw an object from Kong by its 'Kong ID'

        :param client:
        :type client: kong.contract.KongAdminContract
        :param kong_id:
        :type kong_id: uuid.UUID
        :param parent_kong_id: Optional reference to a parent object
        :type parent_kong_id: uuid.UUID
        """

    def on_withdraw(self, client, obj):
        """
        Called to withdraw a KongProxyModel from Kong

        :param client:
        :type client: kong.contract.KongAdminContract
        :param obj:
        :type obj: kong_admin.models.KongProxyModel
        """
        parent_object = self.get_parent_object(obj)

        if obj.kong_id is None:
            return obj

        return self.on_withdraw_by_id(
            client, str(obj.kong_id), str(parent_object.kong_id) if parent_object is not None else None)

    def before_publish(self, client, obj):
        parent_object = self.get_parent_object(obj)

        if obj.kong_id is None:
            return

        if not self.is_published(client, obj.kong_id, parent_object.kong_id if parent_object is not None else None):
            obj.kong_id = None
            self.get_proxy_class().objects.filter(id=obj.id).update(kong_id=obj.kong_id)

    def after_publish(self, client, obj):
        obj.synchronized_at = timezone.now()
        obj.synchronized = True

        # Doing this instead of saving will prevent the save signal from being send out!!!
        self.get_proxy_class().objects.filter(id=obj.id).update(
            synchronized=obj.synchronized, synchronized_at=obj.synchronized_at)

    def before_withdraw(self, client, obj):
        pass

    def after_withdraw(self, client, obj):
        obj.synchronized_at = None
        obj.synchronized = False

        # Doing this instead of saving will prevent the save signal from being send out!!!
        self.get_proxy_class().objects.filter(id=obj.id).update(
            synchronized=obj.synchronized, synchronized_at=obj.synchronized_at)

    def get_parent_object(self, obj):
        """
        Returns a parent object for a given object

        :param obj:
        :return:
        """

    def get_parent_key(self):
        """
        Returns the key that references the parent object
        :return:
        """

    def publish(self, client, obj):
        """
        Publish a KongProxyModel to Kong

        :param client:
        :type client: kong.contract.KongAdminContract
        :param obj:
        :type obj: kong_admin.models.KongProxyModel
        :rtype: kong_admin.models.KongProxyModel
        :return: The KongProxyModel that has been published to Kong
        """
        with transaction.atomic():
            self.before_publish(client, obj)

        kong_id = self.on_publish(client, obj)

        # Always update the kong_id
        obj.kong_id = kong_id
        self.get_proxy_class().objects.filter(id=obj.id).update(kong_id=obj.kong_id)

        with transaction.atomic():
            self.after_publish(client, obj)

        return obj

    def withdraw(self, client, obj):
        """
        Withdraw a KongProxy model from Kong

        :param client:
        :type client: kong.contract.KongAdminContract
        :param obj:
        :type obj: kong_admin.models.KongProxyModel
        :rtype: kong_admin.models.KongProxyModel
        :return: The KongProxyModel that has been withdrawn from Kong
        """
        with transaction.atomic():
            self.before_withdraw(client, obj)

        self.on_withdraw(client, obj)

        # Always update the kong_id
        obj.kong_id = None
        self.get_proxy_class().objects.filter(id=obj.id).update(kong_id=obj.kong_id)

        with transaction.atomic():
            self.after_withdraw(client, obj)

        return obj

    def withdraw_by_id(self, client, kong_id, parent_kong_id=None):
        """
        Withdraw an object from Kong by its 'Kong ID'

        :param client:
        :type client: kong.contract.KongAdminContract
        :param kong_id: The id of the object, as it is known by Kong
        :type kong_id: uuid.UUID
        :rtype: kong_admin.models.KongProxyModel
        :return: The kong_id of the object that has been withdrawn from Kong
        """
        try:
            obj = self.get_proxy_class().objects.get(kong_id=kong_id)
        except self.get_proxy_class().DoesNotExist:
            obj = None

        if obj is not None:
            return self.withdraw(client, obj)

        # We don't have a reference to that API anymore. Just try to remove it remotely
        self.on_withdraw_by_id(client, kong_id, parent_kong_id)
        return obj

    def synchronize(self, client, queryset=None, delete=False):
        """
        :param client: The client to use
        :type client: kong.contract.KongAdminContract
        :param queryset: A queryset containing KongProxyModel objects
        :type queryset: django.db.models.QuerySet.
        :param delete: Whether or not to delete the object in the Kong service, if there is no model.
        :type delete: bool
        :return:
        """

        # Make sure we have a queryset
        queryset = queryset or self.get_proxy_class().objects.all()

        # Delete remote api's that do not exist in this database
        if delete:
            for kong_struct in self.on_retrieve_all(client):
                kong_id = kong_struct.get('id', None)
                assert kong_id is not None

                parent_kong_id = kong_struct.get(self.get_parent_key(), None)

                if not queryset.filter(kong_id=kong_id).exists():
                    logger.debug('synchronize: delete %s by id: %s' % (self.get_proxy_class(), kong_id))
                    self.withdraw_by_id(client, kong_id, parent_kong_id=parent_kong_id)

        # Add remote apis that only exist in this database
        for obj in queryset:
            self.publish(client, obj)

        return queryset

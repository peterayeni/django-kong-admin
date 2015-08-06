# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import logging

from django.utils import timezone

from kong.exceptions import ConflictError

from .models import APIReference, PluginConfigurationReference, PluginConfigurationField

logger = logging.getLogger(__name__)


def publish_api(api_ref, client):
    try:
        api_struct = client.apis.add_or_update(
            api_id=api_ref.api_id, target_url=api_ref.target_url, name=api_ref.name, public_dns=api_ref.public_dns,
            path=api_ref.path, strip_path=api_ref.strip_path)
    except ConflictError:
        api_struct = client.apis.update(
            name_or_id=(api_ref.name or api_ref.public_dns), target_url=api_ref.target_url, name=api_ref.name,
            public_dns=api_ref.public_dns, path=api_ref.path, strip_path=api_ref.strip_path)
    except Exception as e:
        logger.exception('Could not create api: %s', e)
        raise e

    api_ref.api_id = api_struct['id']
    api_ref.synchronized_at = timezone.now()
    api_ref.synchronized = True

    assert api_ref.api_id is not None

    # Doing this instead of saving will prevent the save signal from being send out!!!
    APIReference.objects\
        .filter(id=api_ref.id)\
        .update(api_id=api_ref.api_id, synchronized=api_ref.synchronized, synchronized_at=api_ref.synchronized_at)

    return api_ref


def withdraw_api(api_ref, client):
    assert api_ref.api_id is not None

    client.apis.delete(str(api_ref.api_id))

    api_ref.api_id = None
    api_ref.synchronized_at = None
    api_ref.synchronized = False

    # Doing this instead of saving will prevent the save signal from being send out!!!
    APIReference.objects\
        .filter(id=api_ref.id)\
        .update(api_id=api_ref.api_id, synchronized=api_ref.synchronized, synchronized_at=api_ref.synchronized_at)

    return api_ref


def withdraw_api_by_id(api_id, client):
    assert api_id is not None

    try:
        api_ref = APIReference.objects.get(api_id=api_id)
    except APIReference.DoesNotExist:
        api_ref = None

    if api_ref is not None:
        return withdraw_api(api_ref, client)

    # We don't have a reference to that API anymore. Just try to remove it remotely
    client.apis.delete(str(api_id))


def synchronize_apis(client, queryset=None, delete=False):
    """
    :param client: The client to use
    :type client: kong.contract.KongAdminContract
    :param queryset: A queryset containing APIReference objects
    :type queryset: django.db.models.QuerySet.
    :param delete: Whether or not to delete API's in the Kong service, if there is no model.
    :type delete: bool
    :return:
    """

    # Delete remote api's that do not exist in this database
    if queryset is None and delete:
        for api_struct in client.apis.iterate():
            api_id = api_struct.get('id', None)
            assert api_id is not None
            if not APIReference.objects.filter(api_id=api_id).exists():
                logger.debug('synchronize_apis: delete api by id: %s' % api_id)
                withdraw_api_by_id(api_id, client)

    # Make sure we have a queryset
    queryset = queryset or APIReference.objects.all()

    # Add remote apis that only exist in this database
    for api_ref in queryset:
        publish_api(api_ref, client)

    return queryset


def publish_plugin_configuration(plugin_configuration_ref, client):
    fields = {}

    for field in PluginConfigurationField.objects.filter(configuration=plugin_configuration_ref):
        fields[field.property] = field.value

    consumer_id = plugin_configuration_ref.consumer.id if plugin_configuration_ref.consumer is not None else None

    try:
        plugin_configuration_struct = client.apis.plugins(str(plugin_configuration_ref.api.api_id)).create_or_update(
            plugin_configuration_id=plugin_configuration_ref.plugin_configuration_id,
            plugin_name=plugin_configuration_ref.name, enabled=plugin_configuration_ref.enabled,
            consumer_id=consumer_id, **fields)
    except ConflictError:
        plugin_configuration_struct = client.apis.plugins(str(plugin_configuration_ref.api.api_id)).update(
            plugin_name=plugin_configuration_ref.name, enabled=plugin_configuration_ref.enabled,
            consumer_id=consumer_id, **fields)
    except Exception as e:
        logger.exception('Could not create plugin configuration: %s', e)
        raise e

    plugin_configuration_ref.plugin_configuration_id = plugin_configuration_struct['id']
    plugin_configuration_ref.synchronized_at = timezone.now()
    plugin_configuration_ref.synchronized = True

    assert plugin_configuration_ref.plugin_configuration_id is not None

    # Doing this instead of saving will prevent the save signal from being send out!!!
    PluginConfigurationReference.objects\
        .filter(id=plugin_configuration_ref.id)\
        .update(plugin_configuration_id=plugin_configuration_ref.plugin_configuration_id,
                synchronized=plugin_configuration_ref.synchronized,
                synchronized_at=plugin_configuration_ref.synchronized_at)

    return plugin_configuration_ref


def withdraw_plugin_configuration(plugin_configuration_ref, client):
    assert plugin_configuration_ref.plugin_configuration_id is not None

    client.apis.plugins(str(plugin_configuration_ref.api.api_id)).delete(
        str(plugin_configuration_ref.plugin_configuration_id))

    plugin_configuration_ref.plugin_configuration_id = None
    plugin_configuration_ref.synchronized_at = None
    plugin_configuration_ref.synchronized = False

    # Doing this instead of saving will prevent the save signal from being send out!!!
    PluginConfigurationReference.objects\
        .filter(id=plugin_configuration_ref.id)\
        .update(plugin_configuration_id=plugin_configuration_ref.plugin_configuration_id,
                synchronized=plugin_configuration_ref.synchronized,
                synchronized_at=plugin_configuration_ref.synchronized_at)

    return plugin_configuration_ref


def withdraw_plugin_configuration_by_id(api_id, plugin_configuration_id, client):
    assert plugin_configuration_id is not None

    try:
        plugin_configuration_ref = PluginConfigurationReference.objects.get(
            plugin_configuration_id=plugin_configuration_id)
    except PluginConfigurationReference.DoesNotExist:
        plugin_configuration_ref = None

    if plugin_configuration_ref is not None:
        return withdraw_plugin_configuration(plugin_configuration_ref, client)

    # We don't have a reference to that PluginConfiguration anymore. Just try to remove it remotely
    assert api_id is not None
    client.apis.plugins(api_id).delete(plugin_configuration_id)


def synchronize_plugin_configurations(client, queryset=None, delete=False):
    """
    :param client: The client to use
    :type client: kong.contract.KongAdminContract
    :param queryset: A queryset containing PluginConfigurationReference objects
    :type queryset: django.db.models.QuerySet.
    :param delete: Whether or not to delete Plugin Configuration's in the Kong service, if there is no model.
    :type delete: bool
    :return:
    """

    # Delete remote api's that do not exist in this database
    if queryset is None and delete:
        apis = list(client.apis.iterate())
        for api_struct in apis:
            api_id = api_struct.get('id', None)
            assert api_id is not None

            plugin_configurations = client.apis.plugins(api_id).list(size=100).get('data', None)
            assert plugin_configurations is not None

            for plugin_configuration_struct in plugin_configurations:
                plugin_configuration_id = plugin_configuration_struct.get('id', None)
                assert plugin_configuration_id is not None

                if not PluginConfigurationReference.objects.filter(
                        plugin_configuration_id=plugin_configuration_id).exists():
                    logger.debug('synchronize_plugin_configurations: delete plugin configuration by id: %s' %
                                 plugin_configuration_id)
                    withdraw_plugin_configuration_by_id(plugin_configuration_id, client)

    # Make sure we have a queryset
    queryset = queryset or PluginConfigurationReference.objects.all()

    # Add remote apis that only exist in this database
    for plugin_configuration_ref in queryset:
        publish_plugin_configuration(plugin_configuration_ref, client)

    return queryset

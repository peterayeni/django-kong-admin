# -*- coding: utf-8 -*-
import logging
from six import python_2_unicode_compatible

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from kong.exceptions import ConflictError
from .enums import Plugins

logger = logging.getLogger(__name__)


class KongProxyModel(models.Model):
    kong_id = models.UUIDField(null=True, blank=True, editable=False)

    created_at = models.DateTimeField(_('created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated'), auto_now=True)
    synchronized = models.BooleanField(default=False)
    synchronized_at = models.DateTimeField(_('synchronized'), null=True, blank=True, editable=False)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class APIReference(KongProxyModel):
    target_url = models.URLField()
    name = models.CharField(null=True, blank=True, unique=True, max_length=32)
    public_dns = models.CharField(null=True, blank=True, unique=True, max_length=32)
    path = models.CharField(null=True, blank=True, max_length=32)
    strip_path = models.BooleanField(default=False)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('API Reference')
        verbose_name_plural = _('API References')

    def __str__(self):
        return self.target_url if not self.name else '%s (%s)' % (self.name, self.target_url)

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     self.name = self.name or None  # Don't store empty strings
    #     self.public_dns = self.public_dns or None  # Don't store empty strings
    #     self.path = self.path or None  # Don't store empty strings
    #     super(APIReference, self).save(force_insert=force_insert, force_update=force_update, using=using,
    #                                    update_fields=update_fields)

    def clean(self):
        if not self.public_dns and not self.path:
            raise ValidationError('At least one of the parameters "public_dns" and "path" should be set')

        if self.synchronized_at and not self.api_id:
            raise ValidationError('There should be an api_id parameter')

        if self.api_id and not self.synchronized_at:
            raise ValidationError('There should be a synchronized_at parameter')


@python_2_unicode_compatible
class PluginConfigurationReference(KongProxyModel):
    api = models.ForeignKey(APIReference, related_name='plugins')
    consumer = models.ForeignKey('ConsumerReference', null=True, blank=True, related_name='plugins')
    name = models.CharField(_('Plugin Name'), choices=Plugins.choices(), max_length=32)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Plugin Configuration Reference')
        verbose_name_plural = _('Plugin Configuration References')
        unique_together = [('name', 'api')]

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class PluginConfigurationField(models.Model):
    configuration = models.ForeignKey(PluginConfigurationReference, related_name='fields')
    property = models.CharField(max_length=32)
    value = models.CharField(max_length=32)

    class Meta:
        verbose_name = _('Plugin Configuration Field')
        verbose_name_plural = _('Plugin Configuration Fields')

    def __str__(self):
        return '%s = %s' % (self.property, self.value)


@python_2_unicode_compatible
class ConsumerReference(KongProxyModel):
    username = models.CharField(null=True, blank=True, unique=True, max_length=32)
    custom_id = models.CharField(null=True, blank=True, unique=True, max_length=48)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Consumer Reference')
        verbose_name_plural = _('Consumer References')

    def __str__(self):
        return self.username or self.custom_id

    # def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    #     self.consumer_id = self.consumer_id or None  # Don't store empty strings
    #     self.username = self.username or None  # Don't store empty strings
    #     self.custom_id = self.custom_id or None  # Don't store empty strings
    #     super(ConsumerReference, self).save(
    #         force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def clean(self):
        if not self.username and not self.custom_id:
            raise ValidationError('At least one of the parameters "username" and "custom_id" should be set')


class ConsumerAuthentication(KongProxyModel):
    consumer = models.ForeignKey(ConsumerReference)

    class Meta:
        abstract = True


@python_2_unicode_compatible
class BasicAuthReference(ConsumerAuthentication):
    username = models.CharField(null=True, blank=True, unique=True, max_length=32)
    password = models.CharField(null=True, blank=True, unique=True, max_length=40)

    class Meta:
        verbose_name = _('Basic Auth Reference')
        verbose_name_plural = _('Basic Auth References')

    def __str__(self):
        return 'BasicAuthReference(consumer: %s, username: %s)' % (self.consumer, self.username)


@python_2_unicode_compatible
class KeyAuthReference(ConsumerAuthentication):
    key = models.TextField()

    class Meta:
        verbose_name = _('Key Auth Reference')
        verbose_name_plural = _('Key Auth References')

    def __str__(self):
        key = self.key
        if len(key) > 16:
            key = '%s...' % key[:16]
        return 'KeyAuthReference(consumer: %s, key: %s)' % (self.consumer, key)


@python_2_unicode_compatible
class OAuth2Reference(ConsumerAuthentication):
    name = models.CharField(unique=True, max_length=32)
    redirect_uri = models.URLField()
    client_id = models.CharField(null=True, blank=True, unique=True, max_length=64)
    client_secret = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('OAuth2 Reference')
        verbose_name_plural = _('OAuth2 References')

    def __str__(self):
        return 'OAuth2Reference(name: %s)' % self.name

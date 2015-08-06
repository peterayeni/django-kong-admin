# -*- coding: utf-8 -*-
import logging
from six import python_2_unicode_compatible

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from kong.exceptions import ConflictError
from .enums import Plugins

logger = logging.getLogger(__name__)


class KongProxyModel(models.Model):
    created_at = models.DateTimeField(_('created'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated'), auto_now=True)
    synchronized = models.BooleanField(default=False)
    synchronized_at = models.DateTimeField(_('synchronized'), null=True, blank=True, editable=False)

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.synchronized = False  # Reset synchronized state!
        super(KongProxyModel, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                         update_fields=update_fields)


@python_2_unicode_compatible
class APIReference(KongProxyModel):
    target_url = models.URLField()
    name = models.CharField(null=True, blank=True, unique=True, max_length=32)
    public_dns = models.CharField(null=True, blank=True, unique=True, max_length=32)
    path = models.CharField(null=True, blank=True, max_length=32)
    strip_path = models.BooleanField(default=False)
    api_id = models.UUIDField(null=True, blank=True, editable=False)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('API Reference')
        verbose_name_plural = _('API References')

    def __str__(self):
        return self.target_url if not self.name else '%s (%s)' % (self.name, self.target_url)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.name = self.name or None  # Don't store empty strings
        self.public_dns = self.public_dns or None  # Don't store empty strings
        self.path = self.path or None  # Don't store empty strings
        super(APIReference, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                       update_fields=update_fields)

    def clean(self):
        if not self.public_dns and not self.path:
            raise ValidationError('At least one of the parameters "public_dns" and "path" should be set')

        if self.synchronized_at and not self.api_id:
            raise ValidationError('There should be an api_id parameter')

        if self.api_id and not self.synchronized_at:
            raise ValidationError('There should be a synchronized_at parameter')


@python_2_unicode_compatible
class ConsumerReference(KongProxyModel):
    consumer_id = models.UUIDField(null=True, blank=True, editable=False)
    username = models.CharField(null=True, blank=True, unique=True, max_length=32)
    custom_id = models.CharField(null=True, blank=True, unique=True, max_length=48)
    enabled = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Consumer Reference')
        verbose_name_plural = _('Consumer References')

    def __str__(self):
        return self.username or self.custom_id

    def clean(self):
        if not self.username and not self.custom_id:
            raise ValidationError('At least one of the parameters "username" and "custom_id" should be set')


@python_2_unicode_compatible
class PluginConfigurationReference(KongProxyModel):
    plugin_configuration_id = models.UUIDField(null=True, blank=True, editable=False)
    api = models.ForeignKey(APIReference, related_name='plugins')
    consumer = models.ForeignKey(ConsumerReference, null=True, blank=True, related_name='plugins')
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

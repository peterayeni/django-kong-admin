# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
from contextlib import closing

from django.utils.translation import ugettext_lazy as _
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http.response import HttpResponseRedirect

from .models import APIReference, PluginConfigurationReference, PluginConfigurationField, ConsumerReference, \
    BasicAuthReference, KeyAuthReference, OAuth2Reference
from .factory import get_kong_client, get_api_sync_engine, get_consumer_sync_engine
from .contrib import CustomModelAdmin


@staff_member_required
def synchronize_api_references(request, queryset=None):
    with closing(get_kong_client()) as client:
        try:
            queryset = get_api_sync_engine().synchronize(client, queryset=queryset, delete=True)
        except Exception as e:
            messages.add_message(
                request, messages.ERROR, 'Could not synchronize API References: %s' % str(e))
        else:
            messages.add_message(
                request, messages.SUCCESS, 'Successfully synchronized %d API References (it can take a while before the '
                                           'changes are visible!)' % queryset.count())
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def synchronize_api_reference(request, pk, toggle_enable=False):
    with closing(get_kong_client()) as client:
        obj = APIReference.objects.get(id=pk)
        if (toggle_enable and obj.enabled) or (not toggle_enable and not obj.enabled):
            try:
                obj = get_api_sync_engine().withdraw(client, obj)
                obj.enabled = False
            except Exception as e:
                messages.add_message(
                    request, messages.ERROR, 'Could not withdraw API Reference: %s (was it published?)' % str(e))
            else:
                messages.add_message(
                    request, messages.SUCCESS, 'Successfully withdrawn API Reference (it can take a while before the '
                                               'changes are visible!)')
        else:
            try:
                obj = get_api_sync_engine().publish(client, obj)
                obj.enabled = True
            except Exception as e:
                messages.add_message(request, messages.ERROR, 'Could not publish API Reference: %s' % str(e))
            else:
                messages.add_message(
                    request, messages.SUCCESS, 'Successfully published API Reference (it can take a while before the '
                                               'changes are visible!)')

    if toggle_enable:
        # Updated enabled state without triggering another save
        APIReference.objects.filter(id=pk).update(enabled=obj.enabled)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def synchronize_plugin_configuration_references(request, queryset=None):
    with closing(get_kong_client()) as client:
        try:
            queryset = get_api_sync_engine().plugins().synchronize(client, queryset=queryset, delete=True)
        except Exception as e:
            messages.add_message(
                request, messages.ERROR, 'Could not synchronize Plugin Configuration References: %s' % str(e))
        else:
            messages.add_message(
                request, messages.SUCCESS, 'Successfully synchronized %d Plugin Configuration References (it can take a '
                                           'while before the changes are visible!)' % queryset.count())

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def synchronize_plugin_configuration_reference(request, pk, toggle_enable=False):
    with closing(get_kong_client()) as client:
        obj = PluginConfigurationReference.objects.get(id=pk)

        if toggle_enable:
            obj.enabled = not obj.enabled

        try:
            obj = get_api_sync_engine().plugins().publish(client, obj)
        except Exception as e:
            messages.add_message(
                request, messages.ERROR, 'Could not publish Plugin Configuration Reference: %s' % str(e))
        else:
            messages.add_message(
                request, messages.SUCCESS, 'Successfully published Plugin Configuration Reference (it can take a while '
                                           'before the changes are visible!)')

    # Updated enabled state without triggering another save
    PluginConfigurationReference.objects.filter(id=pk).update(enabled=obj.enabled)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def synchronize_consumer_references(request, queryset=None):
    with closing(get_kong_client()) as client:
        try:
            queryset = get_consumer_sync_engine().synchronize(client, queryset=queryset, delete=True)
        except Exception as e:
            messages.add_message(
                request, messages.ERROR, 'Could not synchronize Consumer References: %s' % str(e))
        else:
            messages.add_message(
                request, messages.SUCCESS, 'Successfully synchronized %d Consumer References (it can take a while before '
                                           'the changes are visible!)' % queryset.count())
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


@staff_member_required
def synchronize_consumer_reference(request, pk, toggle_enable=False):
    with closing(get_kong_client()) as client:
        obj = ConsumerReference.objects.get(id=pk)
        if (toggle_enable and obj.enabled) or (not toggle_enable and not obj.enabled):
            try:
                obj = get_consumer_sync_engine().withdraw(client, obj)
                obj.enabled = False
            except Exception as e:
                messages.add_message(
                    request, messages.ERROR, 'Could not withdraw Consumer Reference: %s (was it published?)' % str(e))
            else:
                messages.add_message(
                    request, messages.SUCCESS, 'Successfully withdrawn Consumer Reference (it can take a while before the '
                                               'changes are visible!)')
        else:
            try:
                obj = get_consumer_sync_engine().publish(client, obj)
                obj.enabled = True
            except Exception as e:
                messages.add_message(request, messages.ERROR, 'Could not publish Consumer Reference: %s' % str(e))
            else:
                messages.add_message(
                    request, messages.SUCCESS, 'Successfully published Consumer Reference (it can take a while before the '
                                               'changes are visible!)')

    if toggle_enable:
        # Updated enabled state without triggering another save
        ConsumerReference.objects.filter(id=pk).update(enabled=obj.enabled)

    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def get_toggle_enable_caption(obj):
    return 'Disable' if obj.enabled else 'Enable'


class APIReferenceAdmin(CustomModelAdmin):
    list_display = ('target_url', 'name', 'public_dns', 'path', 'enabled', 'synchronized', 'kong_id')
    list_display_buttons = [{
        'caption': 'Synchronize',
        'url': 'sync-api-ref/',
        'view': synchronize_api_reference
    }, {
        'caption': get_toggle_enable_caption,
        'url': 'toggle-enable/',
        'view': lambda request, pk: synchronize_api_reference(request, pk, toggle_enable=True)
    }]
    action_buttons = [{
        'caption': 'Synchronize all',
        'url': 'sync-api-refs/',
        'view': synchronize_api_references
    }]
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': ('target_url', 'name', 'public_dns', 'path', 'enabled')
        }),
        (_('Advanced options'), {
            'fields': ('strip_path',)
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(APIReference, APIReferenceAdmin)


class PluginConfigurationFieldInline(admin.StackedInline):
    model = PluginConfigurationField


class PluginConfigurationReferenceAdmin(CustomModelAdmin):
    list_display = ('name', 'api', 'enabled', 'synchronized', 'kong_id')
    list_display_buttons = [{
        'caption': 'Synchronize',
        'url': 'sync-plugin-configuration-ref/',
        'view': synchronize_plugin_configuration_reference
    }, {
        'caption': get_toggle_enable_caption,
        'url': 'toggle-enable/',
        'view': lambda request, pk: synchronize_plugin_configuration_reference(request, pk, toggle_enable=True)
    }]
    action_buttons = [{
        'caption': 'Synchronize all',
        'url': 'sync-plugin-configuration-refs/',
        'view': synchronize_plugin_configuration_references
    }]
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': ('name', 'enabled',)
        }),
        (_('Target'), {
            'fields': ('api', 'consumer')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    inlines = [
        PluginConfigurationFieldInline
    ]
    readonly_fields = ('created_at', 'updated_at')

admin.site.register(PluginConfigurationReference, PluginConfigurationReferenceAdmin)


class BasicAuthInline(admin.StackedInline):
    model = BasicAuthReference
    extra = 0
    fields = ('username', 'password')


class KeyAuthInline(admin.StackedInline):
    model = KeyAuthReference
    extra = 0
    fields = ('key',)

class OAuthInline(admin.StackedInline):
    model = OAuth2Reference
    extra = 0
    fields = ('name', 'redirect_uri', 'client_id', 'client_secret')


class ConsumerReferenceAdmin(CustomModelAdmin):
    list_display = ('username_or_custom_id','enabled', 'synchronized', 'kong_id')
    list_display_buttons = [{
        'caption': 'Synchronize',
        'url': 'sync-consumer-ref/',
        'view': synchronize_consumer_reference
    }, {
        'caption': get_toggle_enable_caption,
        'url': 'toggle-enable/',
        'view': lambda request, pk: synchronize_consumer_reference(request, pk, toggle_enable=True)
    }]
    action_buttons = [{
        'caption': 'Synchronize all',
        'url': 'sync-consumer-refs/',
        'view': synchronize_consumer_references
    }]
    list_select_related = True
    fieldsets = (
        (None, {
            'fields': ('username', 'custom_id', 'enabled')
        }),
        (_('Audit'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')
    inlines = [
        BasicAuthInline,
        KeyAuthInline,
        OAuthInline
    ]

    def username_or_custom_id(self, obj):
        return obj.username or obj.custom_id

admin.site.register(ConsumerReference, ConsumerReferenceAdmin)


# class OAuth2ApplicationAdmin(CustomModelAdmin):
#     list_display = ('name','redirect_uri', 'client_id', 'client_secret')
#     fieldsets = (
#         (None, {
#             'fields': ('name', 'redirect_uri')
#         }),
#         (_('Consumers'), {
#             'fields': ('consumers',)
#         }),
#         (_('Credentials'), {
#             'fields': ('client_id', 'client_secret')
#         }),
#     )
#     raw_id_fields = ('consumers',)
#     readonly_fields = ('created_at', 'updated_at')
#
# admin.site.register(OAuth2Application, OAuth2ApplicationAdmin)

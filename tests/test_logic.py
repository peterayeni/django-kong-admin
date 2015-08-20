from __future__ import unicode_literals, print_function

from django.test import TestCase

from kong_admin import models
from kong_admin.factory import get_kong_client
from kong_admin.logic import publish_api, withdraw_api, withdraw_api_by_id, publish_plugin_configuration, \
    withdraw_plugin_configuration, withdraw_plugin_configuration_by_id

from .factories import APIReferenceFactory

class APIReferenceLogicTestCase(TestCase):
    def setUp(self):
        self.client = get_kong_client()
        self._cleanup_api = []

    def tearDown(self):
        self.client.close()

        for api_ref in self._cleanup_api:
            self.assertTrue(isinstance(api_ref, models.APIReference))
            api_ref = models.APIReference.objects.get(id=api_ref.id)  # reloads!!
            withdraw_api(api_ref, self.client)

    def test_failed(self):
        # Create incomplete api_ref
        api_ref = APIReferenceFactory(
            target_url='http://mockbin.com')

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Try to publish, expect an error
        with self.assertRaises(ValueError):
            publish_api(api_ref, self.client)

        self.assertFalse(api_ref.synchronized)

        # Fix api_ref
        api_ref.public_dns = 'mockbin.com'
        api_ref.save()

        # Publish again
        publish_api(api_ref, self.client)
        self.assertTrue(api_ref.synchronized)

    def test_publish_create(self):
        # Create api_ref
        api_ref = APIReferenceFactory(
            target_url='http://mockbin.com',
            public_dns='mockbin.com')

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish
        publish_api(api_ref, self.client)
        self.assertTrue(api_ref.synchronized)

    def test_publish_update(self):
        # Create api_ref
        api_ref = APIReferenceFactory(
            target_url='http://mockbin.com',
            public_dns='mockbin.com')

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish
        publish_api(api_ref, self.client)
        self.assertTrue(api_ref.synchronized)

        # Update
        api_ref.name = 'Mock Bin'
        api_ref.save()

        # Publish
        publish_api(api_ref, self.client)
        self.assertTrue(api_ref.synchronized)

    def test_withdraw(self):
        # Create api_ref
        api_ref = APIReferenceFactory(
            target_url='http://mockbin.com',
            public_dns='mockbin.com')

        # Publish
        publish_api(api_ref, self.client)
        self.assertTrue(api_ref.synchronized)

        # You can delete afterwards
        withdraw_api(api_ref, self.client)
        self.assertFalse(api_ref.synchronized)

    def _cleanup_afterwards(self, api_ref):
        self._cleanup_api.append(api_ref)
        return api_ref

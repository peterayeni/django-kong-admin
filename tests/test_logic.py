from __future__ import unicode_literals, print_function

from django.test import TestCase

from faker import Factory
from faker.providers import BaseProvider

from kong_admin import models
from kong_admin.factory import get_kong_client, get_api_sync_engine
from kong_admin import logic

from .factories import APIReferenceFactory

# Initialize fake
fake = Factory.create()


# Create a provider for API Names (TODO: This is taken copy-paste from python-kong. Fix duplication!)
class APIInfoProvider(BaseProvider):
    def api_name(self):
        return fake.name().replace(' ', '')

    def api_path(self):
        path = fake.uri_path()
        if not path.startswith('/'):
            path = '/%s' % path
        return path
fake.add_provider(APIInfoProvider)


class APIReferenceLogicTestCase(TestCase):
    def setUp(self):
        self.client = get_kong_client()
        self._cleanup_api = []

    def tearDown(self):
        self.client.close()

        for api_ref in self._cleanup_api:
            self.assertTrue(isinstance(api_ref, models.APIReference))
            api_ref = models.APIReference.objects.get(id=api_ref.id)  # reloads!!
            get_api_sync_engine().withdraw(self.client, api_ref)

    def test_failed(self):
        # Create incomplete api_ref
        api_ref = APIReferenceFactory(target_url=fake.url())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Try to sync, expect an error
        with self.assertRaises(ValueError):
            logic.synchronize_api(self.client, api_ref)

        self.assertFalse(api_ref.synchronized)

        # Fix api_ref
        api_ref.public_dns = fake.domain_name()
        api_ref.save()

        # Sync again
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

    def test_sync_initial(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Sync
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

    def test_sync_update(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Mark for auto cleanup
        self._cleanup_afterwards(api_ref)

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)
        self.assertEqual(result['name'], api_ref.public_dns)

        # Update
        new_name = fake.api_name()
        api_ref.name = new_name
        api_ref.save()

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)
        self.assertEqual(result['name'], new_name)


    def test_withdraw(self):
        # Create api_ref
        api_ref = APIReferenceFactory(target_url=fake.url(), public_dns=fake.domain_name())

        # Publish
        logic.synchronize_api(self.client, api_ref)
        self.assertTrue(api_ref.synchronized)

        # Check kong
        result = self.client.apis.retrieve(api_ref.kong_id)
        self.assertIsNotNone(result)
        self.assertEqual(result['target_url'], api_ref.target_url)
        self.assertEqual(result['public_dns'], api_ref.public_dns)

        # Store kong_id
        kong_id = api_ref.kong_id

        # You can delete afterwards
        get_api_sync_engine().withdraw(self.client, api_ref)
        self.assertFalse(api_ref.synchronized)

        # Check kong
        with self.assertRaises(ValueError):
            result = self.client.apis.retrieve(kong_id)

    def _cleanup_afterwards(self, api_ref):
        self._cleanup_api.append(api_ref)
        return api_ref

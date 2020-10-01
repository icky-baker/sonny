from core.models import StorageServer
from django.test import TestCase


class StorageServerTestCase(TestCase):
    def setUp(self):
        self.server = StorageServer(host="host", port=1234, available_space=124)

    def test_ok(self):
        self.server.update(available_space=30)

        self.assertEqual(StorageServer.objects.first().available_space, 30)

    def test_update_unknown_field(self):
        with self.assertRaises(ValueError):
            self.server.update(some_crazy_field="value")

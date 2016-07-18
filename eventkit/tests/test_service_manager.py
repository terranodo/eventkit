
import json
import sys
import traceback

from django.test import TestCase
from django.core.urlresolvers import reverse

class ServiceManagerTests(TestCase):

    def setUp(self):
        self.user = 'admin'
        self.passwd = 'admin'

    def test_create_conf_from_wms(self):
        """Test registering an indexed WMS
        """
        self.client.login(username='admin', password='admin')

        response = self.client.post(
            reverse('register_service'),
            {
                'service_type': 'WMS',
                'service_url': 'http://test.org/wms',
                'service_name': 'test'
            })
        self.assertEqual(response.status_code, 202)

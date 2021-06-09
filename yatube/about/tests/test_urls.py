from django.test import Client, TestCase
from django.urls import reverse

from common_lib.testutils import AppUrlsTestBase


class AboutUrlsTest(TestCase, AppUrlsTestBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls = [
            {
                'url': reverse('about:author'),
                'link': '/about/author/',
                'login_required': None,
                'template': 'about.html'
            },
            {
                'url': reverse('about:tech'),
                'link': '/about/tech/',
                'login_required': None,
                'template': 'about.html'
            },
        ]

    def setUp(self):
        self.guest_client = Client()

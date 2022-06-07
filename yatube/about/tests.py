from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_urls_client_about_templates(self):
        """Проверка доступности адресов /about/.../ ."""
        templates_url_names = (
            ('/about/author/', 'about/author.html',),
            ('/about/tech/', 'about/tech.html',)
        )
        for address, template in templates_url_names:
            with self.subTest(template=template):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                self.assertTemplateUsed(response, template)

    def test_page_client_about_reverse_name(self):
        """Проверка реверсов /about/.../ ."""
        templates_pages_names = (
            ('about:author', '/about/author/',),
            ('about:tech', '/about/tech/',),
        )
        for reverse_name, url in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(reverse(reverse_name), url)

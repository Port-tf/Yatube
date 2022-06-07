from http import HTTPStatus

from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_urls_client_about_templates(self):
        """Проверка доступности шаблона 404.html."""
        response = self.client.get('/404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

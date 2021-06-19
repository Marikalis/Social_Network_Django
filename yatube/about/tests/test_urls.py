from django.test import Client, TestCase

AUTHOR = '/about/author/'
TECH = '/about/tech/'


class URLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_pages_for_guests(self):
        """Страницы доступны любому пользователю."""
        url_names = [
            AUTHOR,
            TECH
        ]
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            AUTHOR: 'about/author.html',
            TECH: 'about/tech.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Name')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            group=cls.group,
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_names = (
            ('posts:index', None, 'posts/index.html', '/'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html',
             f'/group/{self.group.slug}/'),
            ('posts:profile', (self.user,), 'posts/profile.html',
             f'/profile/{self.user}/'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html',
             f'/posts/{self.post.id}/'),
            ('posts:post_edit', (self.post.id,), 'posts/post_create.html',
             f'/posts/{self.post.id}/edit/'),
            ('posts:post_create', None, 'posts/post_create.html', '/create/'),
        )
        self.login = reverse('users:login')
        self.edit = reverse('posts:post_edit', args=(self.post.id,))

    def test_urls_authorized_client_non_existent_template(self):
        """Проверка на несуществеющий адрес /no_page/ для пользователя."""
        response = self.authorized_client.get('/no_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_template_name_author_client_template(self):
        """reverse использует нужный шаблон для авторизированого
        пользователя, он же автор."""
        for name, arg, template, _ in self.url_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(reverse(name, args=arg))
                self.assertTemplateUsed(response, template)

    def test_reverse_name(self):
        """reverse использует нужный хардурл."""
        for name, arg, _, url in self.url_names:
            with self.subTest(name=name):
                self.assertEqual(reverse(name, args=arg), url)

    def test_reverse_name_authorized_client_template(self):
        """name использует нужный шаблон для авторизированого
        пользователя, не автор поста."""
        zed_client = User.objects.create_user(username='Valli')
        self.authorized_client.force_login(zed_client)
        for name, arg, _, _ in self.url_names:
            with self.subTest(name=name):
                if name == 'posts:post_edit':
                    self.assertRedirects(self.authorized_client.get(
                        reverse(name, args=arg), follow=True),
                        reverse(
                            'posts:post_detail',
                            args=(self.post.id,)
                    ))
                else:
                    self.assertEqual(self.authorized_client.get(
                        reverse(name, args=arg)).status_code, HTTPStatus.OK)

    def test_reverse_anonom_client_template(self):
        """reverse использует нужный шаблон для анонимного
        пользователя."""
        for name, arg, _, url in self.url_names:
            with self.subTest(name=name):
                if name in ('posts:post_edit', 'posts:post_create'):
                    response = self.client.get(
                        reverse(name, args=arg), follow=True)
                    self.assertRedirects(
                        response,
                        f'{self.login}?next={url}'
                    )
                else:
                    response = self.client.get(reverse(name, args=arg))
                    self.assertEqual(response.status_code, HTTPStatus.OK)

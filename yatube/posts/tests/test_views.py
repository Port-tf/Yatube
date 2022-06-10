from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm, CommentForm
from posts.models import Group, Follow, Post, Comment


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Luser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Жили-были',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.user
        )
        cls.no_follow_user = User.objects.create_user(username='Goblin')
        cls.follow_user = User.objects.create_user(username='Gremlin')
        cls.follower = Follow.objects.create(
            user=cls.follow_user, author=cls.user)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.follower_client = Client()
        self.follower_client.force_login(self.follow_user)
        self.no_follower_client = Client()
        self.no_follower_client.force_login(self.no_follow_user)

    def examination_context(self, response, bulevo=False):
        if bulevo:
            object = response.context.get('post')
        else:
            object = response.context['page_obj'][0]
        post_group = object.group
        post_text = object.text
        post_author = object.author
        post_data = object.pub_date
        post_image = object.image
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_data, self.post.pub_date)
        self.assertEqual(post_image, self.post.image)
        self.assertContains(response, text='<img', count=1)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        redict = (
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.id,)),
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for name, arg in redict:
            reverse_name = reverse(name, args=arg)
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], PostForm)
                for value, expected in form_fields.items():
                    with self.subTest(value=value):
                        form_field = (
                            response.context.get('form').fields.get(value)
                        )
                        self.assertIsInstance(form_field, expected)

    def test_add_comment_show_correct_context(self):
        """Шаблон add_comment сформирован с правильным контекстом."""
        form_fields = {'text': forms.fields.CharField}
        response = (self.authorized_client.get(reverse(
            'posts:post_detail',
            args=(self.post.id,)
        )))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)
        self.assertIsInstance(
            response.context.get('form').fields.get('text'),
            form_fields['text']
        )

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse('posts:index')))
        self.examination_context(response)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', args=(self.group.slug,))
        ))
        self.examination_context(response)
        self.assertEqual(
            response.context.get('group'), self.group
        )

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:profile', args=(self.user,)
        )))
        self.examination_context(response)
        self.assertEqual(
            response.context.get('author'),
            self.user
        )

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail',
            args=(self.post.id,)
        )))
        self.examination_context(response, True)
        comment = response.context['comments'][0]
        comment_text = comment.text
        self.assertEqual(comment_text, self.comment.text)

    def test_show_comment_in_page(self):
        """Проверка что комментарий появляется на странице."""
        response = (self.authorized_client.get(reverse(
            'posts:post_detail',
            args=(self.post.id,)
        )))
        count_comments = len(response.context['comments'])
        Comment.objects.create(
            post=self.post,
            text='Еще один тестовый комментарий',
            author=self.user
        )
        response = (self.authorized_client.get(reverse(
            'posts:post_detail',
            args=(self.post.id,)
        )))
        self.assertEqual(len(response.context['comments']), count_comments + 1)

    def test_group_no_post(self):
        """Проверка создания поста"""
        new_group = Group.objects.create(
            title='Тестзаголовок',
            slug='new_group_test',
            description='Жить-быть',
        )
        Post.objects.create(
            author=self.user,
            text='Новый тестовый пост',
            group=self.group,
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(new_group.slug,)
        ))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(len(response.context['page_obj']))

    def test_cache_index_page(self):
        """Тест кэширования index."""
        new_post = Post.objects.create(
            author=self.user,
            text='Новый тестовый пост',
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:index'))
        temp = response.content
        new_post.delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, temp)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response.content, temp)

    def test_follow_index_show_context(self):
        """Шаблон follow_index сформирован с правильным контекстом."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.examination_context(response)

    def test_follow_index_show_cont(self):
        """Шаблон follow сформирован с правильным контекстом."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        count_post_follower = len(response.context['page_obj'])
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        count_post_no_follower = len(response.context['page_obj'])
        Post.objects.create(
            author=self.user,
            text='Новый тестовый пост',
            group=self.group,
        )
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']), count_post_follower + 1)
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            len(response.context['page_obj']), count_post_no_follower)

    def test_follower_to_user(self):
        """Проверка на создание подписчика."""
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        count_post_follower = len(response.context['page_obj'])
        response = self.no_follower_client.get(reverse(
            'posts:profile_follow', args=(self.user,)))
        response = self.no_follower_client.get(reverse('posts:follow_index'))
        self.assertFalse(count_post_follower)
        self.assertTrue(len(response.context['page_obj']))

    def test_follower_delete_to_user(self):
        """Проверка на удаление подписчика."""
        response = self.follower_client.get(reverse('posts:follow_index'))
        count_post_follower = len(response.context['page_obj'])
        response = self.follower_client.get(reverse(
            'posts:profile_unfollow', args=(self.user,)))
        response = self.follower_client.get(reverse('posts:follow_index'))
        self.assertTrue(count_post_follower)
        self.assertFalse(len(response.context['page_obj']))


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Luser')
        cls.follow_user = User.objects.create_user(username='Lower')
        Follow.objects.create(
            user=cls.follow_user, author=cls.user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Жили-были',
        )
        cls.follower_client = Client()
        cls.follower_client.force_login(cls.follow_user)
        for copy_post in range(settings.PAGINATOR_POST_CREATE):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {copy_post}',
                group=cls.group,
            )
        cls.template = (
            ('posts:index', None),
            ('posts:group_list', (cls.group.slug,)),
            ('posts:profile', (cls.user,)),
            ('posts:follow_index', None),
        )
        cls.kortage = (
            ('?page=1', settings.PAGINATOR_POST_LIMIT),
            ('?page=2', settings.PAGINATOR_POST_TEST),
        )

    def test_page_contains_ten_records(self):
        for name, arg in self.template:
            with self.subTest(name=name):
                for page, count in self.kortage:
                    with self.subTest(count=count):
                        response = self.follower_client.get(
                            reverse(name, args=arg) + page)
                        self.assertEqual(
                            len(response.context['page_obj']), count)

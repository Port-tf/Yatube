import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем запись в базе данных для проверки сушествующего Post
        cls.user = User.objects.create_user(username='Luser')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Жили-были',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест текст',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.login_client = Client()
        self.login_client.force_login(self.user)
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

    def test_login_client_create_post_form(self):
        """Валидная форма создает запись в PostForm."""
        tasks_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='small/gif'
        )
        form_data = {
            'text': 'Экспресс текст',
            'group': self.group.id,
            'image': uploaded,
        }
        response = self.login_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', args=(self.user.username,)
        ))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Экспресс текст',
                group=self.group,
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        object = Post.objects.first()
        post_group = object.group
        post_text = object.text
        post_author = object.author
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_text, form_data['text'])
        self.assertEqual(post_author, self.user)

    def test_login_client_post_edit_form(self):
        """Валидная форма создает редактирует в PostForm."""
        tasks_count = Post.objects.count()
        new_group = Group.objects.create(
            title='Новая группа',
            slug='new_group_test',
            description='Опять дожди',
        )
        uploaded = SimpleUploadedFile(
            name='small1.gif',
            content=self.small_gif,
            content_type='small/gif'
        )
        form_data = {
            'text': 'Экспресс',
            'group': new_group.id,
            'image': uploaded,
        }
        response = self.login_client.post(
            reverse(
                'posts:post_edit', args=(self.post.id,)
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.id,)
        ))
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertTrue(
            Post.objects.filter(
                text='Экспресс',
                group=new_group.id,
                author=self.user,
                image='posts/small1.gif'
            ).exists()
        )
        object = Post.objects.first()
        post_group = object.group
        post_text = object.text
        post_author = object.author
        self.assertEqual(post_group, new_group)
        self.assertEqual(post_text, form_data['text'])
        self.assertEqual(post_author, self.user)
        response = self.login_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)
        ))
        self.assertFalse(len(response.context['page_obj']))

    def test_client_create_post_form(self):
        """Аноним не создаст запись в Post."""
        post_count = Post.objects.count()
        response = self.client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')
        self.assertEqual(Post.objects.count(), post_count)

    def test_add_comment_authorizet(self):
        """Валидная форма создает редактирует в CommentForm."""
        comment_count = Comment.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Экспресс комментарий',
            'post': self.post,
        }
        response = self.login_client.post(
            reverse(
                'posts:add_comment', args=(self.post.id,)
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=(self.post.id,)
        ))
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text']
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        comment = Comment.objects.first()
        comment_text = comment.text
        self.assertEqual(comment_text, form_data['text'])

    def test_add_comment_client(self):
        comment_count = Comment.objects.count()
        response = self.client.post(
            reverse(
                'posts:add_comment', args=(self.post.id,)
            )
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/comment/')
        self.assertEqual(Comment.objects.count(), comment_count)

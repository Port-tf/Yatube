from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая пост должен быть больше 15',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовая комментарий'
        )

    def test_models_str_metod(self):
        """Проверяем, что у моделей корректно работает __str__."""
        method_str = (
            (self.group, self.group.title,),
            (self.post, self.post.text[:settings.LIMIT_TEXT_MODEL]),
        )
        for model, expected_object_name in method_str:
            with self.subTest(model=model):
                self.assertEqual(
                    expected_object_name,
                    str(model)
                )

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        field_verboses_post = {
            'text': 'Запись',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        field_verboses_group = {
            'title': 'Сообщество',
            'slug': 'Страница Сообщество',
            'description': 'Описание',
        }
        field_verboses_comment = {
            'post': 'Запись',
            'author': 'Автор',
            'text': 'Ваш комментарий',
            'created': 'Дата публикации комментария',
        }
        for field, expected_value in field_verboses_post.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value
                )
        for field, expected_value in field_verboses_group.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value
                )
        for field, expected_value in field_verboses_comment.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = self.post
        comment = self.comment
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)
        help_text_comment = comment._meta.get_field('text').help_text
        self.assertEqual(help_text_comment, 'Текст комментария')

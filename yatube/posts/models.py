from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Group(models.Model):
    title = models.CharField('Сообщество', max_length=200)
    slug = models.SlugField('Страница Сообщество', unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Дневник'
        verbose_name_plural = 'Дневники'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField('Запись', help_text='Введите текст поста')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Сообщество',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        verbose_name = 'Запись'
        verbose_name_plural = 'Записи'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:settings.LIMIT_TEXT_MODEL]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Запись'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Ваш комментарий', help_text='Текст комментария')
    created = models.DateTimeField(
        'Дата публикации комментария', auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )  # пользователь, который подписывается
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подпишись на меня'
    )  # пользователь, на которого подписывается

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
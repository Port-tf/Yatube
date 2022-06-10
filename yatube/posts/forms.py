from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Текст поста',
            'group': 'Сообщество',
        }
        help_texts = {
            'text': 'Напишите свой пост',
            'group': 'Выберите Группу'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Текст комментария'
        }
        help_texts = {
            'text': 'Напишите свой комментарий'
        }

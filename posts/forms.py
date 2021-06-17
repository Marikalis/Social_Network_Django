from django import forms
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {
            "text": _("Напишите о чем ваш пост"),
            "group": _("Выбeрите группу из списка"),
        }
        widget = {
            "text": Textarea(
                attrs={
                    'placeholder': 'Введите текст'
                }
            )
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Текст комментария'}
        help_texts = {'text': 'Hапишите ваш комментарий'}
        widgets = {'text': forms.Textarea({'rows': 3})}

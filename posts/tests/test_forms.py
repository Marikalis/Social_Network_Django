import shutil
import tempfile

from django import forms

from django.conf import settings
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('index')
NEW_POST = reverse('new_post')
POST_TEXT = 'Тестовый пост'


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет переопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    def setUp(self):
        self.user = User.objects.create_user(username='MarieL')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text=POST_TEXT,
            author=self.user,
        )
        self.group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug'
        )
        self.group_other = Group.objects.create(
            title='Название другой группы',
            description='Описание другой группы',
            slug='test-other-slug'
        )
        self.EDIT_POST = reverse('post_edit', args=[
            self.post.author.username, self.post.id])

        self.POST = reverse('post', args=[
            self.post.author.username, self.post.id])

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_before = set(Post.objects.all())
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_file = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': uploaded_file
        }
        response = self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        list_diff = posts_before ^ posts_after
        self.assertEqual(len(list_diff), 1)
        new_post = list_diff.pop()
        self.assertEqual(new_post.text, POST_TEXT)
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.image, f'posts/{uploaded_file.name}')
        self.assertRedirects(response, INDEX)

    def test_post_edit(self):
        """При редактировании поста изменяется запись в базе данных."""
        text_after_edit = 'Тестовый пост после редактирования'
        form_data = {
            'text': text_after_edit,
            'group': self.group_other.id
        }
        response = self.authorized_client.post(
            self.EDIT_POST,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST)
        post_after_edit = response.context['post']
        self.assertEqual(post_after_edit.text, text_after_edit)
        self.assertEqual(post_after_edit.group, self.group_other)
        self.assertEqual(post_after_edit.author, self.post.author)

    def test_new_post_page_show_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(NEW_POST)
        form_fields = {
            'group': forms.models.ModelChoiceField,
            'text': forms.fields.CharField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

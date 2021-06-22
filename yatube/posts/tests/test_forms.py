import shutil
import tempfile

from django import forms

from django.conf import settings
from django.test import Client, TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from posts.models import Comment, Group, Post, User

INDEX = reverse('index')
NEW_POST = reverse('new_post')
POST_TEXT = 'Тестовый пост'
COMMENT_TEXT = 'Тестовый комментарий'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.user = User.objects.create_user(username='MarieL')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.guest_client = Client()
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
        )
        cls.group = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug'
        )
        cls.group_other = Group.objects.create(
            title='Название другой группы',
            description='Описание другой группы',
            slug='test-other-slug'
        )
        cls.post = Post.objects.create(
            text=POST_TEXT,
            author=cls.user,
        )
        cls.uploaded_file = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.EDIT_POST = reverse('post_edit', args=[
            cls.post.author.username, cls.post.id])
        cls.POST = reverse('post', args=[
            cls.post.author.username, cls.post.id])
        cls.ADD_COMMENT = reverse(
            'add_comment',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_before = set(Post.objects.all())
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': self.uploaded_file
        }
        response = self.authorized_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        posts_after = set(response.context['page'])
        list_diff = posts_before ^ posts_after
        self.assertEqual(len(list_diff), 1)
        new_post = list_diff.pop()
        self.assertEqual(new_post.text, POST_TEXT)
        self.assertEqual(new_post.group, self.group)
        self.assertEqual(new_post.author, self.user)
        self.assertEqual(new_post.image, f'posts/{self.uploaded_file.name}')

    def test_create_post_guest(self):
        """Валидная форма не создает запись в Post от гостя."""
        posts_before = set(Post.objects.all())
        form_data = {
            'text': POST_TEXT,
            'group': self.group.id,
            'image': self.uploaded_file
        }
        self.guest_client.post(
            NEW_POST,
            data=form_data,
            follow=True
        )
        posts_after = set(Post.objects.all())
        list_diff = posts_before ^ posts_after
        self.assertEqual(len(list_diff), 0)

    def test_post_edit(self):
        """При редактировании поста изменяется запись в базе данных."""
        text_after_edit = 'Тестовый пост после редактирования'
        another_uploaded_file = SimpleUploadedFile(
            name='another_small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

        form_data = {
            'text': text_after_edit,
            'group': self.group_other.id,
            'image': another_uploaded_file
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
        self.assertEqual(
            post_after_edit.image,
            f'posts/{another_uploaded_file.name}'
        )

    def test_post_edit_guest(self):
        """При редактировании поста гостем
            не изменяется запись в базе данных."""
        text_after_edit = 'Тестовый пост после редактирования'

        text_before_edit = self.post.text
        group_before_edit = self.post.group
        author_before_edit = self.post.author
        image_before_edit = self.post.image
        another_uploaded_file = SimpleUploadedFile(
            name='another_small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )

        form_data = {
            'text': text_after_edit,
            'group': self.group_other.id,
            'image': another_uploaded_file
        }
        self.guest_client.post(
            self.EDIT_POST,
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.text, text_before_edit)
        self.assertEqual(self.post.group, group_before_edit)
        self.assertEqual(self.post.author, author_before_edit)
        self.assertEqual(
            self.post.image,
            image_before_edit
        )

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

    def test_add_comment(self):
        """Комментарий появляется в базе после добавления
            авторизованным пользователем"""
        comments_before = set(self.post.comments.all())
        form_data = {
            'text': COMMENT_TEXT
        }
        response = self.authorized_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        comments_after = set(response.context['comments'])
        list_diff = comments_before ^ comments_after
        self.assertEqual(len(list_diff), 1)
        new_comment = list_diff.pop()
        self.assertEqual(new_comment.text, COMMENT_TEXT)
        self.assertEqual(new_comment.author, self.user)
        self.assertEqual(new_comment.post, self.post)

    def test_add_comment_guest(self):
        """Комментарий не появляется в базе после добавления гостем"""
        comments_before = set(self.post.comments.all())
        form_data = {
            'text': COMMENT_TEXT
        }
        self.guest_client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        comments_after = set(Comment.objects.filter(post=self.post))
        list_diff = comments_before ^ comments_after
        self.assertEqual(len(list_diff), 0)

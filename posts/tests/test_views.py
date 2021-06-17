import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import Client, TestCase

from posts.models import Group, Post, User
from posts.settings import PAGE_SIZE

INDEX = reverse('index')
NEW_POST = reverse('new_post')
DESCRIPTION = 'Тестовое описание'
USERNAME = 'Test_lisa'
GROUP_WITHOUT_POST_SLAG = 'test-slug-empty'
GROUP_WITH_POST_SLAG = 'test-slug'
PROFILE = reverse(
    'profile',
    kwargs={'username': USERNAME}
)
GROUP_WITH_POSTS = reverse(
    'group_posts',
    kwargs={'slug': GROUP_WITH_POST_SLAG}
)
GROUP_WITHOUT_POSTS = reverse(
    'group_posts',
    kwargs={'slug': GROUP_WITHOUT_POST_SLAG}
)


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group_with_post = Group.objects.create(
            title='Группа с постом',
            description=DESCRIPTION,
            slug=GROUP_WITH_POST_SLAG
        )
        cls.group_without_post = Group.objects.create(
            title='Группа без поста',
            description=DESCRIPTION,
            slug=GROUP_WITHOUT_POST_SLAG
        )
        cls.user = User.objects.create_user(username=USERNAME)
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_file = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group_with_post,
            image=cls.uploaded_file
        )
        cls.VIEW_POST = reverse(
            'post',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id
            }
        )
        cls.POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id
            }
        )

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_posts_correct_context(self):
        """Шаблоны сформированы с правильным контекстом."""
        urls = [
            INDEX,
            GROUP_WITH_POSTS,
            PROFILE,
        ]
        for url in urls:
            with self.subTest(url=url):
                posts = self.authorized_client.get(url).context['page']
                self.assertEqual(len(posts), 1)
                first_post = posts[0]
                self.assertEqual(first_post.text, self.post.text)
                self.assertEqual(first_post.group, self.post.group)
                self.assertEqual(first_post.author, self.post.author)
                self.assertEqual(
                    first_post.image, f'posts/{self.uploaded_file.name}'
                )

    def test_view_post_correct_context(self):
        """Шаблон view_post сформирован с правильным контекстом."""
        urls = [
            self.VIEW_POST,
        ]
        for url in urls:
            one_post = self.authorized_client.get(url).context['post']
            self.assertEqual(one_post, self.post)
            self.assertEqual(one_post.text, self.post.text)
            self.assertEqual(one_post.group, self.post.group)
            self.assertEqual(one_post.author, self.post.author)
            self.assertEqual(
                one_post.image, f'posts/{self.uploaded_file.name}'
            )

    def test_group_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            GROUP_WITH_POSTS
        )
        group = response.context['group']
        expected_group = self.group_with_post
        self.assertEqual(group.title, expected_group.title)
        self.assertEqual(group.slug, expected_group.slug)
        self.assertEqual(group.description, expected_group.description)

    def test_author_correct_context(self):
        """Словарь context, для страницы отдельного поста
        соответствует."""
        urls = [
            self.VIEW_POST,
            PROFILE
        ]
        for url in urls:
            with self.subTest(url=url):
                author = self.authorized_client.get(url).context['author']
                expected_author = self.user
                self.assertEqual(author, expected_author)

    def test_new_post_with_group_doesnt_shown_on_other_group(self):
        response = self.authorized_client.get(
            GROUP_WITHOUT_POSTS
        )
        self.assertNotIn(self.post, response.context['page'])


SECOND_PAGE_ITEMS_COUNT = 1
ITEMS_COUNT = PAGE_SIZE + SECOND_PAGE_ITEMS_COUNT


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(username='testuser')
        for index in range(ITEMS_COUNT):
            note = f"запись номер {index} "
            Post.objects.create(
                text=note,
                author=user
            )

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_content(self):
        response = self.client.get(INDEX)
        self.assertEqual(
            len(response.context.get('page').object_list),
            PAGE_SIZE
        )

    def test_second_page_content(self):
        response = self.client.get(INDEX + '?page=2')
        self.assertEqual(
            len(response.context.get('page').object_list),
            SECOND_PAGE_ITEMS_COUNT
        )


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser')
        post_note = 'Создаем пост'
        Post.objects.create(
            text=post_note,
            author=cls.user
        )

    def setUp(self):
        self.guest_client = Client()

    def test_cache_index_pages(self):
        """Проверяем работу кэша главной страницы."""
        first_response = self.client.get(INDEX)
        anoter_post_note = 'Еще один пост'
        Post.objects.create(
            text=anoter_post_note,
            author=self.user
        )
        response_after_post_add = self.client.get(INDEX)
        self.assertEqual(
            len(first_response.content),
            len(response_after_post_add.content)
        )

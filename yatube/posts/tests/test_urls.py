from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

INDEX = reverse('index')
NEW_POST = reverse('new_post')
FOLLOW_INDEX = reverse('follow_index')
AUTH = reverse('login')
FAKE_PAGE = '/fake/page'
USERNAME = 'testuser'
GROUP_POST_SLAG = 'test-slug'
PROFILE = reverse(
    'profile',
    kwargs={'username': USERNAME}
)
GROUP_POSTS = reverse(
    'group_posts',
    kwargs={'slug': GROUP_POST_SLAG}
)
FOLLOW = reverse(
    'profile_follow',
    kwargs={'username': USERNAME}
)
UNFOLLOW = reverse(
    'profile_unfollow',
    kwargs={'username': USERNAME}
)


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.some_user = User.objects.create_user(username='someuser')
        cls.user = User.objects.create_user(username=USERNAME)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.another_authorized_client = Client()
        cls.another_authorized_client.force_login(cls.some_user)
        cls.group = Group.objects.create(
            title='Тестовое название',
            description='Тестовое описание',
            slug=GROUP_POST_SLAG
        )
        cls.post = Post.objects.create(
            text='a' * 20,
            author=cls.user
        )
        cls.VIEW_POST = reverse(
            'post',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id}
        )
        cls.POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id}
        )
        cls.ADD_COMMENT = reverse(
            'add_comment',
            kwargs={
                'username': cls.post.author.username,
                'post_id': cls.post.id}
        )

    def test_pages_codes(self):
        """Страницы доступны любому пользователю."""
        CODE_SUCCESS = 200
        CODE_REDIRECT = 302
        CODE_NOT_FOUND = 404
        url_names = [
            [self.authorized_client, NEW_POST, CODE_SUCCESS],
            [self.authorized_client, self.POST_EDIT, CODE_SUCCESS],
            [self.authorized_client, self.ADD_COMMENT, CODE_REDIRECT],
            [self.another_authorized_client, FOLLOW, CODE_REDIRECT],
            [self.another_authorized_client, UNFOLLOW, CODE_REDIRECT],
            [self.authorized_client, FOLLOW_INDEX, CODE_SUCCESS],
            [self.another_authorized_client, self.POST_EDIT, CODE_REDIRECT],
            [self.guest_client, INDEX, CODE_SUCCESS],
            [self.guest_client, FOLLOW_INDEX, CODE_REDIRECT],
            [self.guest_client, UNFOLLOW, CODE_REDIRECT],
            [self.guest_client, NEW_POST, CODE_REDIRECT],
            [self.guest_client, self.POST_EDIT, CODE_REDIRECT],
            [self.guest_client, GROUP_POSTS, CODE_SUCCESS],
            [self.guest_client, PROFILE, CODE_SUCCESS],
            [self.guest_client, self.VIEW_POST, CODE_SUCCESS],
            [self.guest_client, self.ADD_COMMENT, CODE_REDIRECT],
            [self.guest_client, FOLLOW, CODE_REDIRECT],
            [self.guest_client, FAKE_PAGE, CODE_NOT_FOUND]
        ]
        for client, url, code in url_names:
            with self.subTest(client=client, url=url, code=code):
                self.assertEqual(
                    code,
                    client.get(url).status_code
                )

    def test_redirect(self):
        """Перенаправление пользователя."""
        templates_url_names = [
            [
                self.another_authorized_client,
                self.POST_EDIT,
                self.VIEW_POST
            ],
            [
                self.guest_client,
                NEW_POST,
                f'{AUTH}?next={NEW_POST}'

            ],
            [
                self.guest_client,
                self.POST_EDIT,
                f'{AUTH}?next={self.POST_EDIT}'
            ],
            [
                self.another_authorized_client,
                self.ADD_COMMENT,
                self.VIEW_POST
            ],
            [
                self.guest_client,
                self.ADD_COMMENT,
                f'{AUTH}?next={self.ADD_COMMENT}'
            ],
            [
                self.guest_client,
                FOLLOW,
                f'{AUTH}?next={FOLLOW}'
            ],
            [
                self.another_authorized_client,
                FOLLOW,
                PROFILE
            ],
            [
                self.guest_client,
                UNFOLLOW,
                f'{AUTH}?next={UNFOLLOW}'
            ],
            [
                self.another_authorized_client,
                UNFOLLOW,
                PROFILE
            ],

        ]
        for client, url, url_redirect in templates_url_names:
            with self.subTest(url=url):
                self.assertRedirects(
                    client.get(url),
                    url_redirect
                )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX: 'index.html',
            NEW_POST: 'new_post.html',
            GROUP_POSTS: 'group.html',
            PROFILE: 'profile.html',
            self.VIEW_POST: 'post.html',
            self.POST_EDIT: 'new_post.html',
            FOLLOW_INDEX: 'follow.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template
                )

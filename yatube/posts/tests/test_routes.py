from django.test import TestCase
from django.urls import reverse

from posts.models import Post, User


INDEX = reverse('index')
NEW_POST = reverse('new_post')


class RoutesTest(TestCase):
    def test_routes(self):
        user = User.objects.create_user(username='testuser')
        group_slug = 'test-slug'
        post = Post.objects.create(
            text='Тестовый пост',
            author=user
        )
        PROFILE = reverse(
            'profile',
            kwargs={'username': user.username}
        )
        GROUP_POSTS = reverse(
            'group_posts',
            kwargs={'slug': group_slug}
        )
        VIEW_POST = reverse(
            'post',
            kwargs={
                'username': post.author.username,
                'post_id': post.id}
        )
        POST_EDIT = reverse(
            'post_edit',
            kwargs={
                'username': post.author.username,
                'post_id': post.id}
        )
        routes_and_urls = [
            [INDEX, '/'],
            [NEW_POST, '/new/'],
            [PROFILE, f'/{user.username}/'],
            [GROUP_POSTS, f'/group/{group_slug}/'],
            [VIEW_POST, f'/{user.username}/{post.id}/'],
            [POST_EDIT, f'/{user.username}/{post.id}/edit/']
        ]
        for route, url in routes_and_urls:
            self.assertEqual(route, url)

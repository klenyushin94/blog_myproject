from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User, Follow


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user1 = User.objects.create_user(username='mike')
        cls.user2 = User.objects.create_user(username='alex')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )
        cls.guest_client = Client()
        cls.authorized_client1 = Client()
        cls.authorized_client2 = Client()
        cls.authorized_author = Client()
        cls.authorized_client1.force_login(PostURLTest.user1)
        cls.authorized_client2.force_login(PostURLTest.user2)
        cls.authorized_author.force_login(PostURLTest.author)

    def setUp(self):
        cache.clear()

    def test_following(self):
        '''Проверка подписки и отписки авторизированным пользователем'''
        follow_count = Follow.objects.count()
        self.authorized_client1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'author'}
            )),
        self.assertNotEqual(Follow.objects.count(), follow_count)
        self.assertTrue(Follow.objects.all().exists())
        self.authorized_client1.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'author'}
            )),
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertFalse(Follow.objects.all().exists())

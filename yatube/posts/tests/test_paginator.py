from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache

from posts.models import Group, Post, User

COUNT_POSTS = 13
FIRST_PAGE = 10
SECOND_PAGE = 3


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.user = User.objects.create_user(username='mike')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        for i in range(COUNT_POSTS):
            cls.post = Post.objects.create(
                author=cls.author,
                text=(f'Тестовый пост {i+1}'),
                group=cls.group
            )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_author = Client()
        cls.authorized_client.force_login(PaginatorViewsTest.user)
        cls.authorized_author.force_login(PaginatorViewsTest.author)
    
    def setUp(self):
        cache.clear()

    def test_index_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице index равно 10."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), FIRST_PAGE)

    def test_index_second_page_contains_three_records(self):
        """Проверка: количество постов на второй странице index равно 3."""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE)

    def test_group_list_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице
        group_list равно 10."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        ))
        self.assertEqual(len(response.context['page_obj']), FIRST_PAGE)

    def test_group_list_second_page_contains_three_records(self):
        """Проверка: количество постов на второй странице
        group_list равно 3."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE)

    def test_profile_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице
        profile равно 10."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'author'}
        ))
        self.assertEqual(len(response.context['page_obj']), FIRST_PAGE)

    def test_profile_second_page_contains_three_records(self):
        """Проверка: количество постов на второй странице
        profile равно 3."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'author'}
        ) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), SECOND_PAGE)

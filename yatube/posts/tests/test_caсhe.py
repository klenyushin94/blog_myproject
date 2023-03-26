from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Comment, Group, Post, User


class PostURLTest(TestCase):
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
        cls.group2 = Group.objects.create(
            title='Тестовая группа2',
            slug='test-slug2',
            description='Тестовое описание2',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )
        cls.post2 = Post.objects.create(
            author=cls.author,
            text='Тестовый пост2',
            group=cls.group2
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_author = Client()
        cls.authorized_client.force_login(PostURLTest.user)
        cls.authorized_author.force_login(PostURLTest.author)

    def setUp(self):
        cache.clear()

    def test_cache(self):
        """Проверка работы кэша через удаление поста"""
        response1 = self.authorized_author.get(reverse('posts:index'))
        post_count = len(response1.context['page_obj'])
        Post.objects.get(id=1).delete()
        self.assertEqual((len(response1.context['page_obj'])), post_count)
        cache.clear()
        response2 = self.authorized_author.get(reverse('posts:index'))
        self.assertEqual((len(response2.context['page_obj'])), post_count - 1)

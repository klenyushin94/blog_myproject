from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Follow, Group, Post, User


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.author2 = User.objects.create_user(username='author2')
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
        cls.post2 = Post.objects.create(
            author=cls.author2,
            text='Тестовый пост2',
            group=cls.group
        )
        cls.guest_client = Client()
        cls.authorized_client1 = Client()
        cls.authorized_client2 = Client()
        cls.authorized_author = Client()
        cls.authorized_author2 = Client()
        cls.authorized_client1.force_login(PostURLTest.user1)
        cls.authorized_client2.force_login(PostURLTest.user2)
        cls.authorized_author.force_login(PostURLTest.author)
        cls.authorized_author2.force_login(PostURLTest.author2)

    def setUp(self):
        cache.clear()

    def test_following(self):
        '''Проверка подписки авторизированным пользователем'''
        self.assertFalse(
            Follow.objects.filter(
                author=PostURLTest.author,
                user_id=PostURLTest.user1.pk
            ).exists()
        )
        self.authorized_client1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTest.author.username}
            )),
        self.assertTrue(
            Follow.objects.filter(
                author=PostURLTest.author,
                user_id=PostURLTest.user1.pk
            ).exists()
        )

    def test_unfollowing(self):
        '''Проверка отписки авторизированным пользователем'''
        Follow.objects.create(
            author=PostURLTest.author,
            user_id=PostURLTest.user1.pk
        )
        self.authorized_client1.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': PostURLTest.author.username}
            )),
        self.assertFalse(
            Follow.objects.filter(
                author=PostURLTest.author,
                user_id=PostURLTest.user1.pk
            ).exists()
        )

    def test_post_in_follow_index_follow(self):
        """Тестовый пост автора отображается у подписанного юзера"""
        Follow.objects.create(
            author=PostURLTest.author,
            user_id=PostURLTest.user1.pk
        )
        response = self.authorized_client1.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = first_object.author
        self.assertEqual(text, PostURLTest.post.text)
        self.assertEqual(author, PostURLTest.post.author)

    def test_post_in_follow_index_no_follow(self):
        """Тестовый пост автора не отображается у не подписанного юзера"""
        Follow.objects.create(
            author=PostURLTest.author,
            user_id=PostURLTest.user1.pk
        )
        Follow.objects.create(
            author=PostURLTest.author2,
            user_id=PostURLTest.user2.pk
        )
        response = self.authorized_client2.get(reverse('posts:follow_index'))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = first_object.author
        self.assertNotEqual(text, PostURLTest.post.text)
        self.assertNotEqual(author, PostURLTest.post.author)

    def test_follow_to_yourself(self):
        """Нельзя подписаться на себя самого"""
        self.authorized_client1.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': PostURLTest.user1.username}
            )),
        self.assertFalse(
            Follow.objects.filter(
                author=PostURLTest.author,
                user_id=PostURLTest.user1.pk
            ).exists()
        )

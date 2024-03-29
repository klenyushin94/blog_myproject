from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Group, Post, User, Comment


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
        pass

    def test_post_in_index(self):
        """Тестовый пост попал на страницу index."""
        response = self.authorized_client.get(reverse('posts:index'))
        i = 0
        for i in range(len(response.context['page_obj'])):
            first_object = response.context['page_obj'][i]
            text = first_object.text
            if text == PostURLTest.post.text:
                self.assertEqual(text, PostURLTest.post.text)

    def test_post_in_group_list(self):
        """Тестовый пост попал на указанную group_list."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        ))
        i = 0
        for i in range(len(response.context['page_obj'])):
            first_object = response.context['page_obj'][i]
            text = first_object.text
            if text == PostURLTest.post.text:
                self.assertEqual(text, PostURLTest.post.text)

    def test_post_in_profile(self):
        """Тестовый пост попал на указанную profile."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'author'}
        ))
        i = 0
        for i in range(len(response.context['page_obj'])):
            first_object = response.context['page_obj'][i]
            text = first_object.text
            if text == PostURLTest.post.text:
                self.assertEqual(text, PostURLTest.post.text)

    def test_post_not_in_group_list(self):
        """Тестовый пост не попал на другую группу."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug2'}
        ))
        i = 0
        for i in range(len(response.context['page_obj'])):
            first_object = response.context['page_obj'][i]
            text = first_object.text
            if text == PostURLTest.post.text:
                self.assertEqual(text, PostURLTest.post.text)

    def test_comment_in_detail(self):
        """Тестовый комментарий попал на detail."""
        response = self.authorized_author.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': '1'}
        ))
        i = 0
        for i in range(len(response.context['comments'])):
            first_object = response.context['comments'][i]
            text = first_object.text
            if text == PostURLTest.post.text:
                self.assertEqual(text, PostURLTest.comment.text)

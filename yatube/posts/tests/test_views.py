import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_author = Client()
        cls.authorized_client.force_login(PostURLTest.user)
        cls.authorized_author.force_login(PostURLTest.author)

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': 'test-slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'mike'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': '1'})
            ),
            'posts/create_post.html': reverse('posts:create'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_edit_uses_correct_template(self):
        """URL-адрес posts/post_edit использует шаблон create_post.html."""
        response = self.authorized_author.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'}
            )
        )
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = first_object.author.username
        image = first_object.image
        self.assertEqual(text, PostURLTest.post.text)
        self.assertEqual(author, PostURLTest.author.username)
        self.assertEqual(image, PostURLTest.post.image)

    def test_group_list_show_correct_context(self):
        """Шаблон group_lost сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'test-slug'}
        ))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = first_object.author.username
        group = first_object.group
        image = first_object.image
        self.assertEqual(text, PostURLTest.post.text)
        self.assertEqual(author, PostURLTest.author.username)
        self.assertEqual(group.title, PostURLTest.group.title)
        self.assertEqual(image, PostURLTest.post.image)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'author'}
        ))
        first_object = response.context['page_obj'][0]
        text = first_object.text
        author = first_object.author.username
        image = first_object.image
        self.assertEqual(text, PostURLTest.post.text)
        self.assertEqual(author, PostURLTest.author.username)
        self.assertEqual(image, PostURLTest.post.image)

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': '1'}
        ))
        first_object = response.context['individual_post']
        text = first_object.text
        author = first_object.author.username
        image = first_object.image
        self.assertEqual(text, PostURLTest.post.text)
        self.assertEqual(author, PostURLTest.author.username)
        self.assertEqual(image, PostURLTest.post.image)

    def test_create_show_correct_context(self):
        """Шаблон create принимает не пустой form."""
        response = self.authorized_client.get(reverse('posts:create'))
        first_object = response.context.get('form')
        self.assertIsNotNone(first_object)

    def test_edit_show_correct_context(self):
        """Шаблон edit принимает не пустой form."""
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': '1'}
        ))
        first_object = response.context.get('form')
        self.assertIsNotNone(first_object)
